#!/usr/bin/env bash

# Все методы полной неопределенности (для метода Гурвича коэф.пессимизма=0.3)
dfs evaluate complete input/complete/economarket.json results/complete/economarket.json general_solution 0.3

# Многокритериальная задача методом стохастической неопределенности
dfs evaluate stochastic input/stochastic/economarket_modified.json  results/stochastic/economarket_modified.json multi_criteria_problem

# Методы попарного доминирования частичной неопределенности
dfs evaluate partial input/partial/economarket.json results/partial/economarket_fishburn.json fishburn
dfs evaluate partial input/partial/economarket.json results/partial/economarket_kirkwood.json kirkwood

# Критерии Вальда и Бернулли-Лапласа при группе [1,4]
dfs evaluate partial input/partial/economarket.json results/partial/economarket_wald.json wald_criterion "[1,4]"
dfs evaluate partial input/partial/economarket.json results/partial/economarket_bernlap.json bernoulli_laplace_criterion "[1,4]"
