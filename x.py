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

def test(test_file=None, args=None):
    """
    Runs pytest on the specified test file.
    If no test file is specified, runs pytest on all test files.
    Additional arguments for pytest can be passed with the args parameter.
    """
    if test_file:
        cmd = f"python -m pytest -k {test_file}"
    else:
        cmd = f"python -m pytest"

    os.system(f"{cmd} {args if args else ''}")

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
    fire.Fire({'run': run, 'test': test, "lint": lint, "autofmt": auto_pep})
