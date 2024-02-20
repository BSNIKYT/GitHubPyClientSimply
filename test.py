import pytest

from main import InitLogin

@pytest.fixture
def init_login():
    return InitLogin(logger=None, login='test_user', password='test_password')

def test_login_success(init_login):
    init_login.login()
    assert init_login.auth == True

def test_login_failure(init_login):
    init_login.login()
    assert init_login.auth == False


