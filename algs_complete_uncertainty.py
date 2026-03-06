""" Методы, рассматриваемые в статье """

import numpy as np
from schemas import CompleteUncertaintyInput, CompleteUncertaintyResult, AllCompleteMethodsResult

'''
Определить формат вывода (сейчас выводим вектор мер и индекс лучших стратегий)
Функция выводит данные в отсортированном порядке в зависимости от направления оптимизации (minimize = True/False)
'''
def _format_measures(measures: np.ndarray, minimize: bool = False) -> tuple[np.ndarray, np.ndarray]:
    if measures.ndim != 1:
        raise ValueError("measures must be a 1-D array (one value per strategy)")

    if minimize:
        measures_s = np.sort(measures)
        best_idx = np.argsort(measures)
    else:
        measures_s = np.sort(measures)[::-1]
        best_idx = np.argsort(-measures)

    best_idx = np.asarray(best_idx, dtype=np.int16) + 1
    return measures_s, best_idx


# 1. Функция пессимизма (Вальда)
def _pessimism(M: np.ndarray):
    measures = M.min(axis=1)
    return _format_measures(measures, minimize=False)


# 2. Функция оптимизма (максимакса)
def _optimism(M: np.ndarray):
    measures = M.max(axis=1)
    return _format_measures(measures, minimize=False)


# 3. Функция пессимизма-оптимизма (Гурвича)
def _hurwich(M: np.ndarray, _u: float):
    M = np.asarray(M, dtype=float)
    u = np.float64(_u)
    measures = u * M.min(axis=1) + (1 - u) * M.max(axis=1)
    return _format_measures(measures, minimize=False)


# 4. Функция Сэвиджа
def _savage(M: np.ndarray):
    M = np.asarray(M, dtype=float)
    regrets = np.abs(M - M.max(axis=0))
    measures = regrets.max(axis=1)
    return _format_measures(measures, minimize=True)


# 5. Функция Бернулли-Лапласа
def _bernulli_laplace(M: np.ndarray):
    M = np.asarray(M, dtype=float)
    measures = M.mean(axis=1)
    return _format_measures(measures, minimize=False)


# 6. Принцип максимального правдоподобия (гибридный)
def _maximum_likelihood(M: np.ndarray, **kwargs):
    n, m = M.shape

    if m == 2:
        return _maximum_likelihood_2d(M)

    # --- m > 2: метод Монте-Карло на симплексе Π0 ---
    return _maximum_likelihood_mc(M, **kwargs)


# Аналитический метод максимального правдоподобия на 2D-пространстве
def _maximum_likelihood_2d(M: np.ndarray):
    M = np.asarray(M, dtype=float)
    n, m = M.shape
    if m != 2:
        raise ValueError("Analytic method requires axis1 equals 2")

    # Собираем точки пересечения прямых E_i(p) = p*a_i + (1-p)*b_i
    points = [0.0, 1.0]
    for i in range(n):
        a_i, b_i = M[i]
        for j in range(i + 1, n):
            a_j, b_j = M[j]

            denom = (a_i - b_i) - (a_j - b_j)
            if abs(denom) < 1e-12:
                # Прямые параллельны или совпадают — пересечения на (0,1) нет
                continue

            p = (b_j - b_i) / denom
            if 0.0 < p < 1.0:
                points.append(p)

    # Упорядочиваем и убираем дубликаты
    points = sorted(set(points))
    lengths = np.zeros(n, dtype=float)

    # Для каждого интервала [left, right] берём середину и смотрим, какая стратегия лучшая
    for left, right in zip(points[:-1], points[1:]):
        mid = 0.5 * (left + right)

        # ожидания E_k(mid)
        payoffs = M[:, 0] * mid + M[:, 1] * (1.0 - mid)
        best = int(np.argmax(payoffs))
        lengths[best] += (right - left)

    # длины интервалов на [0,1] уже суммарно дают 1.0
    return _format_measures(lengths, minimize=False)


# метод Монте-Карло на симплексе Π0
def _maximum_likelihood_mc(M: np.ndarray, n_samples: int = 100_000, seed: int | None = None):
    M = np.asarray(M, dtype=float)
    n, m = M.shape

    rng = np.random.default_rng(seed)
    # Dirichlet(1,...,1) => равномерно по симплексу вероятностей
    P = rng.dirichlet(np.ones(m), size=n_samples)

    # Матожидания для всех стратегий и всех реализаций p:
    # payoffs[s, k] = E_k(p^(s))
    payoffs = P @ M.T

    # Для каждой реализации p^(s) смотрим, какая стратегия даёт максимум
    best_rows = np.argmax(payoffs, axis=1)
    # Частоты попаданий -> оценки мер Π_k
    counts = np.bincount(best_rows, minlength=n)
    measures = counts / n_samples
    return _format_measures(measures, minimize=False)


_METHODS_BY_NAME = {
    "pessimism": _pessimism,
    "optimism": _optimism,
    "hurwich": _hurwich,
    "savage": _savage,
    "bernulli_laplace": _bernulli_laplace,
    "maximum_likelihood": _maximum_likelihood,
    "maximum_likelihood_2d": _maximum_likelihood_2d,
    "maximum_likelihood_mc": _maximum_likelihood_mc
}


def solution(data: CompleteUncertaintyInput, method, *args) -> CompleteUncertaintyResult:
    """
    Универсальная «обёртка» над методами полной неопределённости.
    method может быть как функцией (_pessimism, _optimism, ...), так и строкой
    с именем метода: \"pessimism\", \"optimism\", \"hurwich\", \"savage\",
    \"bernulli_laplace\", \"maximum_likelihood\".
    """
    if isinstance(method, str):
        if method not in _METHODS_BY_NAME:
            raise ValueError(f"Неизвестный метод: {method}")
        method_fn = _METHODS_BY_NAME[method]
    else:
        method_fn = method

    matrix = np.asarray(data.M, dtype=float)
    result = method_fn(matrix, *args)

    return CompleteUncertaintyResult(
        measures=result[0],
        ranks=result[1],
        best_variant=result[1][0]
    )


def general_solution(data: CompleteUncertaintyInput, u:float) -> AllCompleteMethodsResult:
    return AllCompleteMethodsResult(
        pessimism = solution(data, _pessimism),
        optimism = solution(data, _optimism),
        hurwich = solution(data, _hurwich, u),
        savage= solution(data, _savage),
        bernulli_laplace= solution(data, _bernulli_laplace),
        maximum_likelihood= solution(data, _maximum_likelihood)
    )


if __name__ == "__main__":
    import core

    fileinput = "input/ex.json"
    fileoutput = "results/ex1.json"

    core.evaluate(fileinput, fileoutput, general_solution, 0.5,
     input_model=CompleteUncertaintyInput, output_model=AllCompleteMethodsResult)
