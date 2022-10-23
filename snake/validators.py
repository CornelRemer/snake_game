from snake.dynaconf_config import settings


class ConfigValidator:
    @staticmethod
    def register_validator(*validators) -> None:
        for validator in validators:
            settings.validators.register(validator)

    @staticmethod
    def validate_all() -> None:
        settings.validators.validate_all()
