#!/usr/bin/env python

import fire
import os

DEBUG_PORT = 5001


def run(debug=True):
    os.system(f"uvicorn app:app --reload --port={DEBUG_PORT}")


def test(test_file=None):
    if test_file:
        os.system(f"python -m pytest -k {test_file}")
    else:
        os.system(f"python -m pytest")


def lint():
    os.system(
        """find .  -path ./venv -prune -false -o -name "*.py" -exec pylint --extension-pkg-whitelist='pydantic' {} +;"""
    )


if __name__ == '__main__':
    fire.Fire({'run': run, 'test': test, "lint": lint})
