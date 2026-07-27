from pathlib import Path

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke tests")
