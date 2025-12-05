import argparse
import core
import inspect
import algs
import sys


# Интерфейс командной строки
def parse_args():
    parser = argparse.ArgumentParser(
        description="Решение задач из модуля 11 Падиновского (МПР в условиях полной неопределенности)"
    )

    # обязательный аргумент (основной файл)
    parser.add_argument(
        "filename",
        type=str,
        help="Матрица выигрышей (файл в input)"
    )

    # обязательный аргумент (название метода)
    parser.add_argument(
        "method",
        type=str,
        help="Название метода"
    )

    # параметр u - для Гурвича
    parser.add_argument(
        "-u",
        type=float,
        nargs="?",
        help="Показатель пессимизма u: 0<=u<=1"
    )

    # точность
    parser.add_argument(
        "-p", "--precision",
        type=int,
        default=core.precision,
        help="Точность чисел с плавающей точкой (для вывода и правильного тестирования)"
    )

    parser.add_argument(
        "-e", "--eval",
        type=str,
        nargs="?",
        help="Укажите файл записи в results"
    )

    parser.add_argument(
        "-v", "--check",
        type=str,
        nargs="?",
        help="Укажите файл проверки в validate"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Получаем имена всех методов
    functions = {
        name: func for name, func in inspect.getmembers(algs, inspect.isfunction)
        if func.__module__ == 'algs' and not name.startswith('_')
    }

    if args.method == "hurwich":
        if args.u is None:
            raise ValueError("При использовании метода Гурвича необходимо объявить коэф.u")
        if not 0 <= args.u <= 1:
            raise ValueError("Весовой коэф.u должен быть в пределах [0; 1]")
        u = args.u
    else:
        u = None

    if args.eval is not None:
        if u is None:
            core.evaluate(args.filename, args.eval, functions[args.method], args.precision)
        else:
            core.evaluate(args.filename, args.eval, functions[args.method], args.precision, u)
        sys.exit(0)

    if args.check is not None:
        if u is None:
            err_message = core.validate(args.filename, args.check, functions[args.method], args.precision)
        else:
            err_message = core.validate(args.filename, args.check, functions[args.method], args.precision, u)
        assert err_message is None, err_message
        sys.exit(0)

    raise ValueError("Не указан файл: -e/-v <filename> требуется")


if __name__ == '__main__':
    main()