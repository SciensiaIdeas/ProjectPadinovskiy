""" Методы принятия решений в условиях частичной неопределенности """

import re
import numpy as np
import ast


from schemas import (
    PartialUncertaintyInput,
    CompleteUncertaintyResult,
    WaldResult,
    BernoulliLaplaceResult,
)


def _is_multi_criteria(matrix: np.ndarray) -> bool:
    """Проверяет, является ли матрица многокритериальной (3D или элементы — векторы)."""
    if matrix.size == 0:
        return False
    if matrix.ndim == 3:
        return True
    if matrix.ndim == 2:
        sample = matrix.flat[0]
        if isinstance(sample, (list, np.ndarray)) and len(sample) > 1:
            return True
    return False


def _parse_utility_function(utility_str: str):
    """Парсит строку функции полезности (y1, y2, ...) и возвращает callable. Использует numpy."""
    matches = re.findall(r"y(\d+)", utility_str)
    num_args = max((int(m) for m in matches), default=1)
    args_list = [f"y{i + 1}" for i in range(num_args)]
    args_str = ", ".join(args_list)
    safe_globals = {
        "np": np,
        "log": np.log,
        "log2": np.log2,
        "log10": np.log10,
        "sqrt": np.sqrt,
        "exp": np.exp,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "arctan": np.arctan,
        "max": max,
        "min": min,
        "abs": np.abs,
        "sum": sum,
        "round": np.round,
        "pow": np.power,
    }
    code = compile(f"lambda {args_str}: {utility_str}", "<string>", "eval")
    return eval(code, safe_globals, {})


def _build_utility_matrix(input_data: PartialUncertaintyInput) -> np.ndarray:
    """
    Строит 2D матрицу полезности из criteria_matrix.
    Для 3D применяет функцию полезности (utility_expression или сумму по умолчанию).
    """
    raw = np.array(input_data.criteria_matrix, dtype=object)
    if not _is_multi_criteria(raw):
        return np.asarray(raw, dtype=float)

    if input_data.utility_expression:
        ufunc = _parse_utility_function(input_data.utility_expression)
    else:
        ufunc = lambda *args: sum(args)

    n_alt = len(raw)
    n_states = len(raw[0])
    out = np.zeros((n_alt, n_states))
    for i in range(n_alt):
        for j in range(n_states):
            cell = raw[i, j]
            if isinstance(cell, (list, np.ndarray)):
                out[i, j] = ufunc(*cell)
            else:
                out[i, j] = ufunc(cell)
    return out


def _fishburn_dominance(M: np.ndarray, i: int, j: int, ordering_type: str) -> str:
    """Доминирование по теореме Фишберна (12.1 / 12.2)."""
    delta = M[i] - M[j]
    n = len(delta)
    if n > 2:
        cumulative_sums = [np.sum(delta[: k + 1]) for k in range(n)]
    else:
        cumulative_sums = [float(np.sum(delta))]

    all_non_negative = all(cs >= 0 for cs in cumulative_sums)
    at_least_one_positive = any(cs > 0 for cs in cumulative_sums)

    if ordering_type == "strict":
        return "Строгое предпочтение" if (all_non_negative and at_least_one_positive) else "Нет предпочтения"
    # weak
    if all_non_negative and at_least_one_positive:
        return "Строгое предпочтение"
    if all_non_negative:
        return "Нестрогое предпочтение"
    return "Нет предпочтения"


def _mixed_ordering_dominance(M: np.ndarray, i: int, j: int, groups: list[int]) -> str:
    """Доминирование при смешанном упорядочении (теорема 12.3)."""
    delta = M[i] - M[j]
    cumulative_sums = [float(np.sum(delta[:k_r])) for k_r in groups]
    all_non_negative = all(cs >= 0 for cs in cumulative_sums)
    at_least_one_positive = any(cs > 0 for cs in cumulative_sums)
    if all_non_negative and at_least_one_positive:
        return "Строгое предпочтение"
    if all_non_negative:
        return "Нестрогое предпочтение"
    return "Нет предпочтения"


def _calculate_probability_vertices(groups: list[int]) -> list[list[float]]:
    """Вершины многогранника вероятностей по границам групп (формула 1.12)."""
    if not groups:
        raise ValueError("Список групп не может быть пустым")
    n = groups[-1]
    vertices = []
    for k_r in groups:
        vertex = [0.0] * n
        for j in range(k_r):
            vertex[j] = 1.0 / k_r
        vertices.append(vertex)
    return vertices


def _run_pairwise_comparisons(
    M: np.ndarray, ordering_type: str, groups: list[int]
) -> list[tuple[int, int, str]]:
    """Middleware: выполняет попарные сравнения, возвращает список (i, j, dominance)."""
    n_alt = M.shape[0]
    out = []
    for i in range(n_alt):
        for j in range(i + 1, n_alt):
            if ordering_type == "mixed":
                dominance = _mixed_ordering_dominance(M, i, j, groups)
            else:
                dominance = _fishburn_dominance(M, i, j, ordering_type)
            out.append((i + 1, j + 1, dominance))
    return out


def _pairwise_to_ranks(n_alt: int, comparisons: list[tuple[int, int, str]]) -> tuple[list[float], list[int], int]:
    """По результатам попарных сравнений строит measures (счёт доминирований), ranks и best_variant."""
    score = np.zeros(n_alt)
    for i_1based, j_1based, dominance in comparisons:
        if dominance == "Строгое предпочтение":
            score[i_1based - 1] += 1
    # ranks: 1-based индексы от лучшего к худшему (при равенстве по индексу по возрастанию)
    order = np.lexsort((np.arange(n_alt), -score))
    ranks = (order + 1).tolist()
    measures = score.tolist()
    best_variant = int(ranks[0])
    return measures, ranks, best_variant


def fishburn(
    input_data: PartialUncertaintyInput,
    ordering_type: str = "weak",
) -> CompleteUncertaintyResult:
    """
    Попарное доминирование по Фишберну (теоремы 12.1/12.2).

    ordering_type:
      - \"weak\"  — нестрогое упорядочение (Фишберн),
      - \"strict\" — строгое упорядочение (Кирквуд–Сарин для неразбитых групп).
    """
    M = _build_utility_matrix(input_data)
    n_alt, n_states = M.shape

    # groups здесь не используются, важен только ordering_type
    comparisons = _run_pairwise_comparisons(M, ordering_type, groups=[n_states])
    measures, ranks, best_variant = _pairwise_to_ranks(n_alt, comparisons)

    return CompleteUncertaintyResult(
        measures=measures,
        ranks=ranks,
        best_variant=best_variant,
    )


def kirkwood(
    input_data: PartialUncertaintyInput,
    _groups: str | None = None,
) -> CompleteUncertaintyResult:
    """
    Доминирование при смешанном упорядочении (обобщённый критерий Кирквуда–Сарина, теорема 12.3).

    groups: границы групп [k1, k2, ..., kq], где k_q = n (число состояний природы).
    Если не заданы, по умолчанию используется одна группа [n].
    """
    M = _build_utility_matrix(input_data)
    n_alt, n_states = M.shape
    
    if _groups is None:
        groups = [n_states]
    else:
        groups = ast.literal_eval(_groups)

    comparisons = _run_pairwise_comparisons(M, "mixed", groups)
    measures, ranks, best_variant = _pairwise_to_ranks(n_alt, comparisons)

    return CompleteUncertaintyResult(
        measures=measures,
        ranks=ranks,
        best_variant=best_variant,
    )


def wald_criterion(input_data: PartialUncertaintyInput, _groups: str) -> WaldResult:
    """
    Критерий Вальда (максимин) с вершинами множества вероятностей.
    Принимает и возвращает Pydantic-модели.
    """
    groups = ast.literal_eval(_groups)
    M = _build_utility_matrix(input_data)
    n_alt, n_states = M.shape
    vertices = _calculate_probability_vertices(groups)
    min_values = []
    for i in range(n_alt):
        min_expected = min(np.dot(M[i], v) for v in vertices)
        min_values.append(float(min_expected))
    optimal_idx = int(np.argmax(min_values)) + 1
    return WaldResult(
        optimal_alternative=optimal_idx,
        min_values=min_values,
        n_alternatives=n_alt,
        n_states=n_states,
        groups=groups,
    )


def bernoulli_laplace_criterion(
    input_data: PartialUncertaintyInput, _groups: str
) -> BernoulliLaplaceResult:
    """
    Критерий Бернулли-Лапласа (равномерное распределение на множестве вероятностей).
    Принимает и возвращает Pydantic-модели.
    """
    groups = ast.literal_eval(_groups)
    M = _build_utility_matrix(input_data)
    n_alt, n_states = M.shape
    vertices = _calculate_probability_vertices(groups)
    center = np.mean(vertices, axis=0)
    expected_values = [float(np.dot(M[i], center)) for i in range(n_alt)]
    optimal_idx = int(np.argmax(expected_values)) + 1
    return BernoulliLaplaceResult(
        optimal_alternative=optimal_idx,
        expected_values=expected_values,
        n_alternatives=n_alt,
        n_states=n_states,
        groups=groups,
    )
