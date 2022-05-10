import argparse
import functools
from pathlib import Path
from typing import Callable, List, Optional

import click
import pyfiglet
from dbt.flags import PROFILES_DIR
from rich.console import Console

from dbt_coves import __version__
from dbt_coves.config.config import DbtCovesConfig
from dbt_coves.core.exceptions import MissingDbtProject
from dbt_coves.tasks.base import BaseTask
from dbt_coves.ui.traceback import DbtCovesTraceback
from dbt_coves.utils.flags import DbtCovesFlags
from dbt_coves.utils.log import logger

# TASKS


console = Console()


def shared_opts(func: Callable) -> Callable:
    """Here we define the options shared across subcommands
    Args:
        func (Callable): Wraps a subcommand
    Returns:
        Callable: Subcommand with added options
    """

    # TODO: Grandfathered in but suboptimal
    @click.option(
        "--log-level",
        envvar="LOGGING_LEVEL",
        show_envvar=True,
        help="Logging level for module execution",
        type=click.STRING,
    )
    @click.option(
        "-v",
        "--verbose",
        help="When provided the length of the tracebacks will not be truncated.",
        default=False,
        is_flag=True,
        type=click.BOOL,
    )
    @click.option(
        "--config-path",
        envvar="DBT_COVES_CONFIG",
        show_envvar=True,
        help="Full path to .dbt_coves.yml file if not using default. Default is current working directory.",
        default="./",
        type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    )
    @click.option(
        "--project-dir",
        envvar="DBT_PROJECT_DIR",
        show_envvar=True,
        help="Which directory to look in for the dbt_project.yml file. Default is the current working directory and its parents.",
        default="./",
        type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    )
    @click.option(
        "--profiles-dir",
        envvar="DBT_PROFILES_DIR",
        show_envvar=True,
        help="Which directory to look in for the profiles.yml file.",
        default=PROFILES_DIR,
        type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    )
    @click.option(
        "-t",
        "--target",
        metavar="PROFILE",
        type=str,
        help="Which profile to load. Overrides setting in dbt_project.yml.",
    )
    @click.option(
        "--vars",
        type=str,
        help="Supply variables to your dbt_project.yml file. This argument should be a YAML string, eg. '{my_variable: my_value}'",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def handle(parser: argparse.ArgumentParser, cli_args: List[str] = list()) -> int:
    main_parser = DbtCovesFlags(parser)
    main_parser.parse_args(cli_args=cli_args)

    if not main_parser.task_cls:
        raise MissingCommand(main_parser.cli_parser)
    else:
        task_cls: BaseTask = main_parser.task_cls

    # set up traceback manager fo prettier errors
    DbtCovesTraceback(main_parser)

    coves_config = None
    if task_cls.needs_config:
        coves_config = DbtCovesConfig(main_parser)
        coves_config.load_config()

    if main_parser.log_level == "debug":
        log_manager.set_debug()

    return task_cls.get_instance(main_parser, coves_config=coves_config).run()


@click.group()
@click.version_option(__version__)
def cli():
    """CLI tool for dbt users applying analytics engineering best practices.

    Select one of the available sub-commands with --help to find out more about them.
    """
    pass


@cli.command("version")
def version():
    """Print version to console, runs on every command by default"""
    from dbt import version

    logo_str = str(pyfiglet.figlet_format("dbt-coves", font="standard"))
    console.print(logo_str, style="cyan")
    dbt_version = version.get_installed_version().to_version_string(skip_matcher=True)
    console.print(
        f"dbt-coves v{__version__}".ljust(24) + f"dbt v{dbt_version}\n".rjust(23)
    )


@cli.command("init")
@shared_opts
def init(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("generate")
@shared_opts
def generate(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("fix")
@shared_opts
def fix(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("check")
@shared_opts
def check(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("setup")
@shared_opts
def setup(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("extract")
@shared_opts
def extract(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


@cli.command("load")
@shared_opts
def load(
    config_path: Path = Path.cwd(),
    project_dir: Path = Path.cwd(),
    profiles_dir: Path = PROFILES_DIR,
    target: Optional[str] = None,
    vars: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
):
    ...


if __name__ == "__main__":
    import dbt.tracking

    dbt.tracking.do_not_track()
    exit(cli())
