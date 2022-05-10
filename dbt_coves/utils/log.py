import logging
from functools import lru_cache

from rich.logging import RichHandler


@lru_cache(maxsize=5)
def logger(log_level: int = logging.INFO, debug: bool = False):
    logger = logging.getLogger("dbt-coves")
    resolved_log_level = log_level if not debug else logging.DEBUG
    logger.setLevel(resolved_log_level)
    rich_handler = RichHandler(
        rich_tracebacks=True,
        show_level=False,
        markup=True,
        enable_link_path=False,
        show_path=False,
    )
    rich_handler.setLevel(resolved_log_level)
    logger.addHandler(rich_handler)
    return logger
