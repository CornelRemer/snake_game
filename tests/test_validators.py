from unittest.mock import patch

import pytest
from dynaconf import Dynaconf, ValidationError, Validator

from snake.validators import ConfigValidator


@pytest.fixture(name="test_settings")
def fixture_test_settings() -> Dynaconf:
    return Dynaconf(settings_files=["tests/fixtures/test_settings.toml"])


class TestConfigValidator:
    def test_register_validator(self, test_settings: Dynaconf):
        validator = Validator("test_settings", is_type_of=str, must_exist=True)
        with patch(target="snake.validators.settings", new=test_settings) as mocked_settings:
            ConfigValidator.register_validator(validator)
            assert validator in mocked_settings.validators

    def test_validate_all_for_valid_settings(self, test_settings: Dynaconf):
        validator = Validator("test_settings", is_type_of=str, must_exist=True)
        with patch(target="snake.validators.settings", new=test_settings):
            ConfigValidator.register_validator(validator)
            ConfigValidator.validate_all()

    def test_validate_all_raises_exception(self, test_settings: Dynaconf):
        validator = Validator("missing_settings", is_type_of=str, must_exist=True)
        with pytest.raises(ValidationError), patch(target="snake.validators.settings", new=test_settings):
            ConfigValidator.register_validator(validator)
            ConfigValidator.validate_all()
