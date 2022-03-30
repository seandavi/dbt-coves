import os
from pathlib import Path

from rich.console import Console
from dbt_coves.tasks.base import NonDbtBaseTask

from .ssh import SetupSSHTask
from .git import SetupGitTask
from .dbt import SetupDbtTask
from .vs_code import SetupVscodeTask
from .sqlfluff import SetupSqlfluffTask
from .pre_commit import SetupPrecommitTask

console = Console()


class SetupAllTask(NonDbtBaseTask):
    """
    Task that runs ssh key generation, git repo clone and db connection setup
    """

    key_column_with = 50
    value_column_with = 30

    @classmethod
    def register_parser(cls, sub_parsers, base_subparser):
        subparser = sub_parsers.add_parser(
            "all",
            parents=[base_subparser],
            help="Sets up SSH keys, git repo, and db connections.",
        )
        subparser.add_argument(
            "--templates",
            type=str,
            help="Location of your sqlfluff, ci and pre-commit config files",
        )
        subparser.set_defaults(cls=cls, which="all")
        return subparser

    def run(self) -> int:
        """
        Env vars that can be set: USER_FULLNAME, USER_EMAIL, WORKSPACE_PATH, GIT_REPO_URL, DBT_PROFILES_DIR
        """
        workspace_path = os.environ.get("WORKSPACE_PATH", Path.cwd())

        SetupSSHTask.run()

        SetupGitTask.run(workspace_path)

        context = SetupDbtTask.get_dbt_profiles_context()

        SetupDbtTask.run_dbt_init()

        SetupVscodeTask.run(context)

        SetupSqlfluffTask(self.args, self.coves_config).run()

        SetupPrecommitTask(self.args, self.coves_config).run()

        SetupDbtTask.dbt_debug()

        return 0

    def get_config_value(self, key):
        return self.coves_config.integrated["setup"]["all"][key]