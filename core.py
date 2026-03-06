""" Основная логика модуля (чтение, запись, тестирование...) """

import os
import json
from typing import Any, Type
from numbers import Real

import numpy as np
from pydantic import BaseModel

'''
Базовые утилиты:
- legacy-режим: работа с матрицей выигрышей NxM (для algs_complete_uncertainty)
- универсальный режим: Pydantic-модели для входа/выхода (для стохастических задач и пр.)
'''

# Точность вывода precision (Важно при тестировании!!)
precision = 2


def read_json(path_parts: str):
    """Чтение JSON из файла."""
    path = os.path.join(path_parts)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data, indent: int = 4) -> None:
    """Запись данных в JSON-файл. path — путь относительно корня проекта."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def _round_floats(obj: Any, _precision: int) -> Any:
    """Рекурсивно округляет все float-значения в структуре до заданной точности."""
    if isinstance(obj, (float, np.floating)):
        return round(obj, _precision)
    if isinstance(obj, list):
        return [_round_floats(v, _precision) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_round_floats(v, _precision) for v in obj)
    if isinstance(obj, dict):
        return {k: _round_floats(v, _precision) for k, v in obj.items()}
    return obj


def _equal_with_tol(a: Any, b: Any, tol: float) -> bool:
    """Сравнение двух структур с допуском tol для чисел."""
    # Числа (любые Real, включая numpy.float64) сравниваем по модулю разности
    if isinstance(a, Real) and isinstance(b, Real):
        # Добавляем небольшой эпсилон, чтобы учесть двоичную погрешность
        return abs(float(a) - float(b)) <= tol + 1e-12

    # Списки / кортежи – поэлементно
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(_equal_with_tol(x, y, tol) for x, y in zip(a, b))

    # Словари – по ключам и значениям
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_equal_with_tol(a[k], b[k], tol) for k in a.keys())

    # Остальное – обычное сравнение
    return a == b


# Выполнение метода (input -> results)
def evaluate(
    filename_read: str,
    filename_write: str,
    method,
    *method_args,
    _precision: int = precision,
    input_model: Type[BaseModel],
    output_model: Type[BaseModel],
) -> None:
    """
    Универсальный запуск метода.

    - Если input_model / output_model не заданы → legacy-режим:
      читаем из input/<filename_read> матрицу 'M', вызываем method(np.array(M), *args),
      результат интерпретируем как (measures_s, best_idx) и пишем в results/<filename_write>.

    - Если заданы Pydantic-модели:
      * читаем JSON из input/<filename_read>
      * создаём input_model и передаём его в method
      * ожидаем output_model (или dict, приводимый к ней)
      * все float-поля округляем до _precision и пишем в results/<filename_write>.
    """
    # --- режим с Pydantic-моделями ---
    if input_model is None or output_model is None:
        raise ValueError("И input_model, и output_model должны быть заданы одновременно")

    raw_in = read_json(filename_read)
    inp = input_model(**raw_in)

    res = method(inp, *method_args)
    if isinstance(res, BaseModel):
        out_model = res
    else:
        out_model = output_model(**res)

    data = out_model.model_dump()
    data_rounded = _round_floats(data, _precision)

    write_json(filename_write, data_rounded)
    return


# Тестирование метода (input, validate -> message | None)
def validate(
    filename_read: str,
    filename_check: str,
    method,
    *method_args,
    _precision: int = precision,
    input_model: Type[BaseModel],
    output_model: Type[BaseModel],
) -> str | None:
    """
    Универсальная проверка метода.

    - Legacy-режим (без моделей):
      сравнение (measures_s, best_idx) с эталоном из validate/<filename_check>.

    - Режим Pydantic:
      * читаем входной JSON → input_model
      * читаем эталонный JSON → output_model
      * запускаем method(input_model, *args)
      * сравниваем структуры model_dump() эталона и результата;
        все float-поля предварительно округляем до _precision.
    """
    # --- режим с Pydantic-моделями ---
    if input_model is None or output_model is None:
        raise ValueError("И input_model, и output_model должны быть заданы одновременно")

    raw_in = read_json(filename_read)
    raw_check = read_json(filename_check)

    inp = input_model(**raw_in)
    expected_model = output_model(**raw_check)

    res = method(inp, *method_args)
    if isinstance(res, BaseModel):
        actual_model = res
    else:
        actual_model = output_model(**res)

    expected = _round_floats(expected_model.model_dump(), _precision)
    actual = _round_floats(actual_model.model_dump(), _precision)

    # Допуск для чисел: разрешаем расхождения до 1 * 10^{-precision}
    tol = 10 ** (-_precision)
    if not _equal_with_tol(expected, actual, tol):
        return (
            "Проверка Pydantic-результата провалилась:\n"
            f"ожидалось: {expected}\n"
            f"получено: {actual}"
        )

    return None