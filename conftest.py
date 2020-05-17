import pytest


def pytest_addoption(parser):
    parser.addoption('--longtests',
                     action='store_true',
                     help='run long tests that are skipped by default')


@pytest.fixture
def longtests(request):
    return request.config.getoption('--longtests')
