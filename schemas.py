from typing import Dict, List, Tuple, Union
from pydantic import BaseModel

"""Pydantic-схемы для стохастической неопределенности."""

class Problem10_3Input(BaseModel):
    """Входные данные для задачи 10.3 (фирма «Русский сыр»)."""

    demand: List[int]
    demand_probs: List[float]
    cost: float
    price: float
    n_values: List[int]


class Problem10_3Result(BaseModel):
    """Результат работы алгоритма problem_10_3."""

    payoff_table: List[List[float]]
    results: List[Dict[str, float | int]]
    ranked: List[Dict[str, float | int]]
    dominance_m_s: List[Tuple[int, int]]
    fsd_dominance: List[Tuple[int, int]]
    ssd_dominance: List[Tuple[int, int]]
    best_candidates: List[int]
    dominance_type: str
    cdf_table: List[Dict[str, float | int]]


class MultiCriteriaInput(BaseModel):
    """Входные данные для многокритериальной задачи."""

    alternatives: List[str]
    states_of_nature: List[str]
    state_probabilities: List[float]
    criteria_values: Dict[str, List[List[float]]]
    aspiration_levels: List[float]
    minimize_criteria: List[int] | None = None
    criteria_descriptions: List[str] | None = None


class MultiCriteriaResult(BaseModel):
    """Результат многокритериальной задачи."""

    results: Dict[str, float]
    best_variant: str
    sorted_results: List[Tuple[str, float]]


"""Pydantic-схемы для полной неопределенности."""

class CompleteUncertaintyInput(BaseModel):
    """Обобщенный формат входных данных для каждой задачи полной неопр.
    (классическая матрица выигрышей). M как список списков, чтобы избежать
    некорректного определения типа при парсинге JSON (numpydantic давал str)."""

    M: List[List[float]]

class CompleteUncertaintyResult(BaseModel):
    """Обобщенный формат выходных данных для каждой задачи полной неопр.:
    веса, ранги, лучшая альтернатива"""

    measures: List[int | float]
    ranks: List[int]
    best_variant: int

class AllCompleteMethodsResult(BaseModel):
    """Все методы полной неопр."""

    pessimism: CompleteUncertaintyResult
    optimism: CompleteUncertaintyResult
    hurwich: CompleteUncertaintyResult
    savage: CompleteUncertaintyResult
    bernulli_laplace: CompleteUncertaintyResult
    maximum_likelihood: CompleteUncertaintyResult


"""Pydantic-схемы для частичной неопределенности."""


class PartialUncertaintyInput(BaseModel):
    """Входные данные для задач частичной неопределенности.
    criteria_matrix: 2D (альтернативы × состояния) или 3D (альтернативы × состояния × критерии).
    """

    criteria_matrix: Union[List[List[float]], List[List[List[float]]]]
    utility_expression: str | None = None


class WaldResult(BaseModel):
    """Результат критерия Вальда (максимин)."""

    method: str = "wald"
    optimal_alternative: int
    min_values: List[float]
    n_alternatives: int
    n_states: int
    groups: List[int]


class BernoulliLaplaceResult(BaseModel):
    """Результат критерия Бернулли-Лапласа."""

    method: str = "bernoulli_laplace"
    optimal_alternative: int
    expected_values: List[float]
    n_alternatives: int
    n_states: int
    groups: List[int]


MODEL_LIST = {
    'problem_10_3': (Problem10_3Input, Problem10_3Result),
    'multi_criteria_problem': (MultiCriteriaInput, MultiCriteriaResult),
    'bernoulli_laplace_criterion': (PartialUncertaintyInput, BernoulliLaplaceResult),
    'wald_criterion': (PartialUncertaintyInput, WaldResult),
    'fishburn': (PartialUncertaintyInput, CompleteUncertaintyResult),
    'kirkwood': (PartialUncertaintyInput, CompleteUncertaintyResult),
    'solution': (CompleteUncertaintyInput, CompleteUncertaintyResult),
    'general_solution': (CompleteUncertaintyInput, AllCompleteMethodsResult)
}