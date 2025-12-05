""" Основная логика модуля (чтение, запись, тестирование...) """

import numpy as np
import os

'''
Входные данные: матрица выигрышей NxM
Выходные данные: матрица 2xN (вектор весов, вектор наилучших стратегий соответственно)
'''

# Точность вывода precision (Важно при тестировании!!)
precision = 2

# Выполнение метода (input -> results)
def evaluate(filename_read, filename_write, method, _precision, *args) -> None:
    path = os.path.join('input', filename_read)
    data_input = np.loadtxt(path)

    # -> measures_s, best_idx
    res = method(data_input, *args)

    # Нужен единый тип данных для вывода
    _format = f"%.{_precision}f"
    str_vec1 = [_format % x for x in res[0]]
    str_vec2 = [str(x) for x in res[1]]

    result_h = np.vstack((str_vec1, str_vec2), dtype=str)

    path = os.path.join('results', filename_write)
    np.savetxt(path, result_h, fmt="%s")


# Тестирование метода (input, validate -> test_result)
def validate(filename_read, filename_check, method, _precision, *args) -> str | None:
    path = os.path.join('input', filename_read)
    data_input = np.loadtxt(path)
    path = os.path.join('validate', filename_check)
    data_check = np.loadtxt(path)

    vec1, vec2 = data_check
    vec1 = np.asarray(vec1, dtype=np.float32)
    vec2 = np.asarray(vec2, dtype=np.int16)

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