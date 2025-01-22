from sshared.config.blocks import UvicornBlock


def get_uvicorn_params_from_config(config: UvicornBlock, /) -> dict:
    return {
        "host": config.host,
        "port": config.port,
        "workers": config.workers,
        "reload": config.mode == "DEBUG",
        "log_level": "info" if config.mode == "DEBUG" else "warning",
        "access_log": config.mode == "DEBUG",
    }
