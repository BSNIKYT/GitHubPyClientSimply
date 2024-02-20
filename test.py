import pytest

from main import InitLogin
from main import InCodeLogger

@pytest.fixture
def init_login():
    return InitLogin(InCodeLogger(), 'test_user', 'test_password')


def test_login_success(init_login):
    init_login.login()
    assert init_login.auth == True

def test_login_failure(init_login):
    init_login.login()
    assert init_login.auth == False


