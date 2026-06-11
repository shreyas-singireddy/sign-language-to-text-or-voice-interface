from config.config import PROJECT_NAME, SUPPORTED_LANGUAGES


def test_config_project_name():
    assert PROJECT_NAME == "SignBridge AI"
    assert "English" in SUPPORTED_LANGUAGES
    assert "Hindi" in SUPPORTED_LANGUAGES
