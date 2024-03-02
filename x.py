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
        cmd = f"python -m pytest -x -k {name}"
    else:
        cmd = f"python -m pytest -x"

    exec_str = f"{cmd} {args if args else ''}"
    print("executing: ", exec_str)
    os.system(exec_str)


def coverage(name=None, open=False):
    """
    Runs pytest with coverage and generates a coverage report.

    if open is True, opens the coverage report in the default web browser.
    """
    base = "python -m coverage run --source=routes -m pytest"
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
    # return success to system since cli
    return 0


def testtest(arg=None):
    import requests
    arg = str(arg)

    base_url = "localhost:5001"

    if arg == "0":
        url = f"http://{base_url}/commands/create"

        payload = {
            "device_id": "72038484-5095-44ba-8a6e-a17bbd9c88a1",
            "args": "args",
            "name": "Test",
            "issuer_id": "ee9470de-54a4-419c-b34a-ba2fa18731d8"
        }

    elif arg == "4":
        url = f"http://{base_url}/commands/create"

        payload = {
            "device_id": "72038484-5095-44ba-8a6e-a17bbd9c88a1",
            "args": "open .",
            "name": "ShellCmd",
            "issuer_id": "ee9470de-54a4-419c-b34a-ba2fa18731d8"
        }

    elif arg == "1":
        url = f"http://{base_url}/devices/register"

        payload = {
            "device_name": "name",
            "issuer_id": "ee9470de-54a4-419c-b34a-ba2fa18731d8",
            "user_id": "ee9470de-54a4-419c-b34a-ba2fa18731d8"
        }

    elif arg == "3":
        # register user
        url = f"http://{base_url}/users/register"

        payload = {
            "name": "name",
            "email": "email",
            "raw_password": "raw_password",
            "subscription_id": "subscription_id",
            "tenant_id": "tenant_id",
            "role_id": "role_id",
            "user_type": "USER"
        }

    elif arg == "2":
        url = f"http://{base_url}/commands/batch/get/all"
        payload = {"device_id": "123"}
        print("firing: ", url, payload)
        response = requests.get(url, params=payload)
        print(response.json())
        print(response.status_code)
        return

    else:
        print("Invalid argument, arg:", arg)
        return

    print("firing: ", url, payload)
    response = requests.post(url, json=payload)
    print(response.json())
    print(response.status_code)


if __name__ == '__main__':
    fire.Fire({'run': run, 'test': test, "lint": lint,
              "autofmt": auto_pep, "coverage": coverage, "testtest": testtest})
