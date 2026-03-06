import core
import inspect
import sys

import algs_complete_uncertainty
import algs_stochastic_uncertainty
import algs_partial_uncertainty
from schemas import MODEL_LIST

import typer
from pathlib import Path
from enum import Enum

# Корень проекта (каталог с cli.py / pyproject.toml) — пути разрешаются относительно него
PROJECT_ROOT = Path(__file__).resolve().parent

# Интерфейс командной строки
app = typer.Typer()

class Module(str, Enum):
    complete = "complete"
    partial = "partial"
    stochastic = "stochastic"


METHODS = {
    "complete": {
        name: func for name, func in inspect.getmembers(algs_complete_uncertainty, inspect.isfunction)
        if func.__module__ == 'algs_complete_uncertainty' and not name.startswith('_')
    },
    "partial": {
        name: func for name, func in inspect.getmembers(algs_partial_uncertainty, inspect.isfunction)
        if func.__module__ == 'algs_partial_uncertainty' and not name.startswith('_')
    },
    "stochastic": {
        name: func for name, func in inspect.getmembers(algs_stochastic_uncertainty, inspect.isfunction)
        if func.__module__ == 'algs_stochastic_uncertainty' and not name.startswith('_')
    }
}

MODULE_NAMES = [m.value for m in Module]


def module_autocomplete(incomplete: str):
    """Completion for module (complete / partial / stochastic)."""
    return [m for m in MODULE_NAMES if m.startswith(incomplete)]


def method_autocomplete(ctx: typer.Context, args: list[str], incomplete: str):
    """Completion for method name. Module is taken from ctx.params if set, else from args."""
    # Prefer parsed module from context (when Click has already parsed previous args)
    module = None
    if ctx.params is not None:
        mod = ctx.params.get("module")
        if mod is not None:
            module = mod.value if hasattr(mod, "value") else mod
    if module is None and args:
        # Fallback: find which word is a module name (args may be full CLI or command positionals)
        for word in args:
            if word in METHODS:
                module = word
                break
    if module not in METHODS:
        return []
    methods = METHODS[module]
    return [m for m in methods if m.startswith(incomplete)]


@app.command()
def validate(
             module: Module = typer.Argument(..., autocompletion=module_autocomplete),
             input_file: Path = typer.Argument(...),
             output_file: Path = typer.Argument(...),
             method: str = typer.Argument(..., autocompletion=method_autocomplete),
             p: int = typer.Option(core.precision, "-p"),
             args: list[str] = typer.Argument(None)):

    method_pointer = METHODS[module][method]
    input_model, output_model = MODEL_LIST[method]
    input_path = str(PROJECT_ROOT / input_file)
    output_path = str(PROJECT_ROOT / output_file)
    err_message = core.validate(input_path, output_path, method_pointer, *(args or []),
                  _precision=p,
                  input_model=input_model, output_model=output_model)
    assert err_message is None, err_message
    print("Success: validation passed")
    sys.exit(0)


@app.command()
def evaluate(
             module: Module = typer.Argument(..., autocompletion=module_autocomplete),
             input_file: Path = typer.Argument(...),
             output_file: Path = typer.Argument(...),
             method: str = typer.Argument(..., autocompletion=method_autocomplete),
             p: int = typer.Option(core.precision, "-p"),
             args: list[str] = typer.Argument(None)):

    method_pointer = METHODS[module][method]
    input_model, output_model = MODEL_LIST[method]
    input_path = str(PROJECT_ROOT / input_file)
    output_path = str(PROJECT_ROOT / output_file)
    core.evaluate(input_path, output_path, method_pointer, *(args or []),
                  _precision=p,
                  input_model=input_model, output_model=output_model)
    sys.exit(0)