import logging
import logging.config
from pathlib import Path
from config.settings import LOG_DIR

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": LOG_DIR / "info.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "file_debug": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOG_DIR / "debug.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file_info", "file_error", "file_debug"],
            "level": "DEBUG",
            "propagate": True
        },
        "src": {
            "handlers": ["console", "file_info", "file_error", "file_debug"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

def setup_logging():
    """Setup logging configuration"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    return logger