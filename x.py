#!/usr/bin/env python

import fire
import os

DEBUG_PORT = 5001


def run(debug=True):
    """
    Runs the application on a specified debug port.
    If debug is True, the application will automatically reload on code changes.
    """
    os.system(f"uvicorn app:app --reload --port={DEBUG_PORT}")


def test(name=None, args=None):
    """
    Runs pytest on the specified test file.
    If no test file is specified, runs pytest on all test files.
    Additional arguments for pytest can be passed with the args parameter.
    """
    if name:
        cmd = f"python -m pytest -k {name}"
    else:
        cmd = f"python -m pytest"

    exec_str = f"{cmd} {args if args else ''}"
    print("executing: ", exec_str)
    os.system(exec_str)

def coverage(name=None, open=False):
    """
    Runs pytest with coverage and generates a coverage report.
    
    if open is True, opens the coverage report in the default web browser.
    """
    base = "python -m coverage run --source=routes,utils -m pytest"
    if name:
        cmd = f"{base} -k {name}"
    else:
        cmd = base
    
    print("executing: ", cmd)
    os.system(cmd)

    if open:
        os.system("python -m coverage html")
        os.system("open 'htmlcov/index.html'")



def lint():
    """
    Runs pylint on all Python files in the current directory and its subdirectories,
    excluding those in the venv directory.
    """
    os.system(
        """find .  -path ./venv -prune -false -o -name "*.py" -exec pylint --extension-pkg-whitelist='pydantic' {} +;"""
    )


def auto_pep():
    """
    Runs autopep8 on all Python files in the current directory and its subdirectories,
    excluding those in the venv directory.
    """
    os.system(
        """find .  -path ./venv -prune -false -o -name "*.py" -exec autopep8 --aggressive --in-place {} +;"""
    )


if __name__ == '__main__':
    fire.Fire({'run': run, 'test': test, "lint": lint, "autofmt": auto_pep, "coverage": coverage})
