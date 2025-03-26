from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "src"
    LOG_FORMAT: str = (
        "%(levelprefix)s | %(asctime)s | %(funcName)s | %(message)s"  # noqa
    )
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = True

    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }

    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }

    def model_dump(self):
        return {
            "version": self.version,
            "disable_existing_loggers": self.disable_existing_loggers,
            "formatters": self.formatters,
            "handlers": self.handlers,
            "loggers": self.loggers,
        }
