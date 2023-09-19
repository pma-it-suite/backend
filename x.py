#!/usr/bin/env python

import fire
import os

DEBUG_PORT = 5001


def run(debug=True):
    os.system(f"uvicorn app:app --reload --port={DEBUG_PORT}")


if __name__ == '__main__':
    fire.Fire(run)
