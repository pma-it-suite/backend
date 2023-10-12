#!/usr/bin/env python

import fire
import os

DEBUG_PORT = 5001


def run(debug=True):
    os.system(f"uvicorn app:app --reload --port={DEBUG_PORT}")


def test(test_file=None, args=None):
    if test_file:
        cmd = f"python -m pytest -k {test_file}"
    else:
        cmd = f"python -m pytest"

    os.system(f"{cmd} {args if args else ''}")


def lint():
    os.system(
        """find .  -path ./venv -prune -false -o -name "*.py" -exec pylint --extension-pkg-whitelist='pydantic' {} +;"""
    )


def auto_pep():
    os.system(
        """find .  -path ./venv -prune -false -o -name "*.py" -exec autopep8 --aggressive --in-place {} +;"""
    )


if __name__ == '__main__':
    fire.Fire({'run': run, 'test': test, "lint": lint, "autofmt": auto_pep})
