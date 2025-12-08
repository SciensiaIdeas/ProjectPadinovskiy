""" Основная логика модуля (чтение, запись, тестирование...) """

import numpy as np
import os
import json

'''
Входные данные: матрица выигрышей NxM
Выходные данные: матрица 2xN (вектор весов, вектор наилучших стратегий соответственно)
'''

# Точность вывода precision (Важно при тестировании!!)
precision = 2

# Выполнение метода (input -> results)
def evaluate(filename_read, filename_write, method, _precision, *args) -> None:
    # читаем матрицу выигрышей
    path = os.path.join('input', filename_read)
    with open(path, 'r') as f:
        d = json.load(f)
        data_input = np.array(d['M'])

    # -> measures_s, best_idx
    res = method(data_input, *args)
    result_h = {'measures_s': np.round(res[0], _precision).tolist(), 'best_idx': res[1].tolist()}

    path = os.path.join('results', filename_write)
    with open(path, 'w') as f:
        json.dump(result_h, f, indent=4)


# Тестирование метода (input, validate -> message | None)
def validate(filename_read, filename_check, method, _precision, *args) -> str | None:
    # читаем матрицу и результаты
    path = os.path.join('input', filename_read)
    with open(path, 'r') as f:
        d = json.load(f)
        data_input = np.array(d['M'])

    path = os.path.join('validate', filename_check)
    with open(path, 'r') as f:
        data_check = json.load(f)

    vec1 = np.asarray(data_check['measures_s'], dtype=np.float64)
    vec2 = np.asarray(data_check['best_idx'], dtype=np.int16)

    # -> measures_s, best_idx
    res = method(data_input, *args)

    # Проверка ранжирования (integer-сравнение)
    if not np.all(res[1] == vec2):
        return f"Проверка ранжирования провалилась:\n получено {res[1]}, а должно быть {vec2}"

    # Проверка весов (float-сравнение)
    atol = 0.5 * 10 ** (-_precision)
    if not np.allclose(res[0], vec1, atol=atol, rtol=0.0):
        return f"Проверка весов провалилась:\n получено {res[0]}, а должно быть {vec1}"

    # Нет ошибки - для assert validate(...) is None
    return None