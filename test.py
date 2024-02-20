# test.py

import pytest
from unittest.mock import MagicMock
from init_login import InitLogin, GitHubLoginError, GitHubDirrectoryNotfoundError

@pytest.fixture
def init_login_instance():
    logger_mock = MagicMock()
    init_login = InitLogin(logger_mock, 'test_login', 'test_password')
    yield init_login
    init_login.quit()

def test_login_success(init_login_instance):
    assert init_login_instance.auth == True

def test_change_repository(init_login_instance):
    init_login_instance.change_repository('https://github.com/BSNIKYT/SvodkaDZ')
    assert init_login_instance.driver.current_url == 'https://github.com/BSNIKYT/SvodkaDZ'

def test_download_zip_archive_success(init_login_instance):
    result = init_login_instance.download_zip_archive('https://github.com/BSNIKYT/SvodkaDZ')
    assert result == True

def test_download_zip_archive_failure(init_login_instance):
    with pytest.raises(GitHubDirrectoryNotfoundError):
        init_login_instance.download_zip_archive('https://github.com/nonexistent_repo')

def test_login_failure():
    logger_mock = MagicMock()
    with pytest.raises(GitHubLoginError):
        InitLogin(logger_mock, 'invalid_login', 'invalid_password')
