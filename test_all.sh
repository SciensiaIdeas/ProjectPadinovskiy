#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR

tests=(
# Полная неопределенность
"dfs validate complete input/complete/example.json validate/complete/example.json general_solution 0.75"
"dfs validate complete input/complete/task4a.json validate/complete/task4a.json general_solution 0.75"
"dfs validate complete input/complete/task4b.json validate/complete/task4b.json general_solution 0.5"
"dfs validate complete input/complete/task6.json validate/complete/task6.json general_solution 0.5"
"dfs validate complete input/complete/task8.json validate/complete/task8.json general_solution 0.75"

"dfs validate complete input/complete/task7.json validate/complete/task7.json solution maximum_likelihood"

# Сравнение 2D и многомерной реализации максимального правдоподобия
"dfs validate complete input/complete/example_ml.json validate/complete/example_ml.json solution maximum_likelihood_2d"
"dfs validate complete input/complete/example_ml.json validate/complete/example_ml.json solution maximum_likelihood_mc"


# Вероятностная неопределенность
"dfs validate stochastic input/stochastic/problem_10_3.json validate/stochastic/problem_10_3.json problem_10_3"
"dfs validate stochastic input/stochastic/problem_13_2.json validate/stochastic/problem_13_2.json multi_criteria_problem"
# Пример из статьи (по инициативе Регины Н.)
"dfs validate stochastic input/stochastic/problem_chemistry_systems.json validate/stochastic/problem_chemistry_systems.json multi_criteria_problem"


# Частичная неопределенность
"dfs validate partial input/partial/task12.json validate/partial/task12_2.json fishburn"
"dfs validate partial input/partial/task12.json validate/partial/task12_3.json kirkwood"
"dfs validate partial input/partial/task12.json validate/partial/task12_7.json wald_criterion \"[1,3,4]\""
"dfs validate partial input/partial/task12.json validate/partial/task12_8.json bernoulli_laplace_criterion \"[1,3,4]\""
"dfs validate partial input/partial/task13.json validate/partial/task13_7.json fishburn"
)

printf "%s\n" "${tests[@]}" \
| pv -l -s ${#tests[@]} \
| while read -r cmd
do
    eval "$cmd" > /dev/null
done


echo "All tests passed"
exit 0
