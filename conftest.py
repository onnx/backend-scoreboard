import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--csvdir", action="store", default="", help="csvdir: dir to which to write test coverage csv"
    )


@pytest.fixture
def csvdir(request):
    return request.config.getoption("--csvdir")


