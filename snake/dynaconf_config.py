from dynaconf import Dynaconf

ROOT_PATH = "config/dynaconf/"

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[
        ROOT_PATH + "game.toml",
        ROOT_PATH + "window.toml",
    ],
)
