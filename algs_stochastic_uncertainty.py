""" Методы принятия решений в условиях стохастической неопределенности """

import numpy as np
from scipy import integrate

from schemas import (
    Problem10_3Input,
    Problem10_3Result,
    MultiCriteriaInput,
    MultiCriteriaResult,
)


def _profit(price: float, cost: float, n: int, d: int) -> float:
    return (price - cost) * min(n, d) - cost * max(0, n - d)


def _build_payoff_table(demand: list, n_values: list, price: float, cost: float) -> np.ndarray:
    """Платёжная матрица U(n, d)."""
    payoff_table = np.zeros((len(n_values), len(demand)))
    for i, n in enumerate(n_values):
        for j, d in enumerate(demand):
            payoff_table[i, j] = _profit(price, cost, n, d)
    return payoff_table


def _expected_and_semideviation(payoff_table: np.ndarray, probs: np.ndarray, n_values: list) -> list:
    """Математическое ожидание и среднее полуотклонение по каждой стратегии."""
    results = []
    for i, n in enumerate(n_values):
        payoffs = payoff_table[i, :]
        expected_value = np.sum(probs * payoffs)
        deviations = np.maximum(0, expected_value - payoffs)
        semi_deviation = np.sum(probs * deviations)
        results.append({
            'n': n,
            'm': round(expected_value, 2),
            's⁻': round(semi_deviation, 2)
        })
    return results


def _cdf_table(payoff_table: np.ndarray, probs: np.ndarray, n_values: list) -> list:
    """Таблица CDF F(y|n) = P(U ≤ y) по всем y и n."""
    all_payoffs = sorted(set(payoff_table.flatten()))
    cdf_data = []
    for payoff_val in all_payoffs:
        row = {'y': float(payoff_val)}
        for i, n in enumerate(n_values):
            payoffs = payoff_table[i, :]
            cdf = np.sum(probs * (payoffs <= payoff_val))
            row[f'n={n}'] = round(cdf, 3)
        cdf_data.append(row)
    return cdf_data


def _make_cdf_func(payoffs: np.ndarray, probs: np.ndarray):
    return lambda y: np.sum(probs * (payoffs <= y))


def _check_fsd(cdf1, cdf2, values: list) -> bool:
    """cdf1 доминирует по FSD над cdf2 ⟺ cdf1(y) ≤ cdf2(y) для всех y."""
    for val in values:
        if cdf1(val) > cdf2(val):
            return False
    return True


def _check_ssd(cdf1, cdf2, values: list, m1: float, m2: float, atol: float = 1e-3) -> bool:
    """
    Проверка SSD: m1 ≥ m2 и интеграл ∫(F2(y) − F1(y)) dy неотрицателен.
    Интегрирование выполняется численно с помощью scipy.integrate.quad.
    """
    if m1 < m2:
        return False

    if not values:
        return False

    a = min(values)
    b = max(values)

    def diff(y: float) -> float:
        return float(cdf2(y) - cdf1(y))

    integral, _ = integrate.quad(diff, a, b, epsabs=1e-6, epsrel=1e-6, limit=200)
    return integral >= -atol


def problem_10_3(input_data: Problem10_3Input) -> Problem10_3Result:
    """
    Задача 10.3 (Фирма «Русский сыр»): матрица прибыли, m–s⁻, FSD/SSD, выбор стратегии.
    Принимает и возвращает Pydantic-модели.
    """
    demand = input_data.demand
    probs = np.array(input_data.demand_probs)
    cost = input_data.cost
    price = input_data.price
    n_values = input_data.n_values

    payoff_table = _build_payoff_table(demand, n_values, price, cost)
    results = _expected_and_semideviation(payoff_table, probs, n_values)
    ranked = sorted(results, key=lambda x: (-x['m'], x['s⁻']))

    all_payoffs = sorted(set(payoff_table.flatten()))
    cdf_funcs = {}
    for i, n in enumerate(n_values):
        cdf_funcs[n] = _make_cdf_func(payoff_table[i, :], probs)

    # Доминирование по m–s⁻
    dominance_m_s = []
    for i in range(len(results)):
        for j in range(len(results)):
            if i != j:
                ri, rj = results[i], results[j]
                if (ri['m'] >= rj['m'] and ri['s⁻'] <= rj['s⁻'] and
                        (ri['m'] > rj['m'] or ri['s⁻'] < rj['s⁻'])):
                    dominance_m_s.append((ri['n'], rj['n']))

    # FSD
    fsd_dominance = []
    for n1 in n_values:
        for n2 in n_values:
            if n1 != n2 and _check_fsd(cdf_funcs[n1], cdf_funcs[n2], all_payoffs):
                fsd_dominance.append((n1, n2))

    # SSD
    ssd_dominance = []
    for n1 in n_values:
        for n2 in n_values:
            if n1 != n2:
                m1 = next(r['m'] for r in results if r['n'] == n1)
                m2 = next(r['m'] for r in results if r['n'] == n2)
                if _check_ssd(cdf_funcs[n1], cdf_funcs[n2], all_payoffs, m1, m2):
                    ssd_dominance.append((n1, n2))

    best_candidates = []
    dominance_type = ""

    fsd_dominant_n = list(set(n1 for n1, _ in fsd_dominance))
    if fsd_dominant_n:
        all_other_n = [n for n in n_values if n not in fsd_dominant_n]
        universal_fsd = [c for c in fsd_dominant_n
                         if all((c, o) in fsd_dominance for o in all_other_n)]
        if universal_fsd:
            best_candidates = universal_fsd
            dominance_type = "FSD"

    if not best_candidates and ssd_dominance:
        dominance_count = {n: sum(1 for n1, n2 in ssd_dominance if n1 == n) for n in n_values}
        max_dom = max(dominance_count.values())
        if max_dom > 0:
            best_candidates = [n for n, c in dominance_count.items() if c == max_dom]
            dominance_type = "SSD"

    if not best_candidates:
        best_candidates = [ranked[0]['n']]
        dominance_type = "m-s⁻ критерий"

    cdf_data = _cdf_table(payoff_table, probs, n_values)

    return Problem10_3Result(
        payoff_table=payoff_table.tolist(),
        results=results,
        ranked=ranked,
        dominance_m_s=dominance_m_s,
        fsd_dominance=fsd_dominance,
        ssd_dominance=ssd_dominance,
        best_candidates=best_candidates,
        dominance_type=dominance_type,
        cdf_table=cdf_data,
    )


def multi_criteria_problem(input_data: MultiCriteriaInput) -> MultiCriteriaResult:
    """
    Многокритериальная задача с уровнями притязаний и вероятностями состояний.
    Принимает и возвращает Pydantic-модели.
    """
    alternatives = input_data.alternatives
    states_of_nature = input_data.states_of_nature
    state_probabilities = input_data.state_probabilities
    criteria_values = input_data.criteria_values
    aspiration_levels = input_data.aspiration_levels
    minimize_criteria = input_data.minimize_criteria or []

    num_criteria = len(aspiration_levels)
    probabilities = {s: state_probabilities[i] for i, s in enumerate(states_of_nature)}
    results = {}

    for variant in alternatives:
        success_prob = 0.0
        for i, state in enumerate(states_of_nature):
            values = criteria_values[variant][i]
            all_met = True
            for j in range(num_criteria):
                value, threshold = values[j], aspiration_levels[j]
                if j in minimize_criteria:
                    all_met = all_met and (value <= threshold)
                else:
                    all_met = all_met and (value >= threshold)
            if all_met:
                success_prob += probabilities[state]
        results[variant] = round(success_prob, 6)

    best_variant = max(results, key=results.get)
    sorted_results = sorted(results.items(), key=lambda x: -x[1])

    return MultiCriteriaResult(
        results=results,
        best_variant=best_variant,
        sorted_results=[(v, p) for v, p in sorted_results],
    )