""" Методы, рассматриваемые в статье """

import numpy as np


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

    best_idx = np.asarray(best_idx, dtype=np.int16)
    return measures_s, best_idx


# 1. Функция пессимизма (Вальда)
def pessimism(M: np.ndarray):
    measures = M.min(axis=1)
    return _format_measures(measures, minimize=False)


# 2. Функция оптимизма (максимакса)
def optimism(M: np.ndarray):
    measures = M.max(axis=1)
    return _format_measures(measures, minimize=False)


# 3. Функция пессимизма-оптимизма (Гурвича)
def hurwich(M: np.ndarray, u: float):
    M = np.asarray(M, dtype=float)
    measures = u * M.min(axis=1) + (1 - u) * M.max(axis=1)
    return _format_measures(measures, minimize=False)


# 4. Функция Сэвиджа
def savage(M: np.ndarray):
    M = np.asarray(M, dtype=float)
    regrets = np.abs(M - M.max(axis=0))
    measures = regrets.max(axis=1)
    return _format_measures(measures, minimize=True)


# 5. Функция Бернулли-Лапласа
def bernulli_laplace(M: np.ndarray):
    M = np.asarray(M, dtype=float)
    measures = M.mean(axis=1)
    return _format_measures(measures, minimize=False)


# 6. Принцип максимального правдоподобия (гибридный)
def maximum_likelihood(M: np.ndarray, **kwargs):
    n, m = M.shape

    if m == 2:
        return maximum_likelihood_2d(M)

    # --- m > 2: метод Монте-Карло на симплексе Π0 ---
    return maximum_likelihood_mc(M, **kwargs)


# Аналитический метод максимального правдоподобия на 2D-пространстве
def maximum_likelihood_2d(M: np.ndarray):
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
def maximum_likelihood_mc(M: np.ndarray, n_samples: int = 100_000, seed: int | None = None):
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