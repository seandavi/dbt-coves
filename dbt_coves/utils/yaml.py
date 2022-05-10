"""Contains yaml related utils which might get used in places."""

from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Dict

from ruamel.yaml import YAML

from dbt_coves.core.exceptions import YAMLFileEmptyError


@lru_cache(maxsize=1)
def open_yaml(path: Path) -> Dict[str, Any]:
    """Open a YAML file.

    Args:
        path (Path): Full filename path pointing to the yaml file we want to open.

    Returns:
        Dict[str, Any]: A python dict containing the content from the yaml file.
    """
    if path.is_file():
        contents = YAML().load(path)
        if contents:
            return contents
        raise YAMLFileEmptyError(f"The following file {path.resolve()} seems empty.")
    raise FileNotFoundError(f"File {path.resolve()} was not found.")


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Serializes a json-like object to a yaml string and writes to file.

    Args:
        path (Path): Full filename path pointing to the yaml file we want to save.
        data (dict[str, Any]): Data to save in the file.
    """
    YAML().dump(data, path)


class YamlHandler:
    def __init__(self, path: Path):
        self._path = path
        self.config = open_yaml(path)

    @property
    def path(self):
        return self._path

    def save(self) -> None:
        """Save the YAML file handled by this class"""
        save_yaml(self.path)

    def prop(self, value: str):
        """Use this to wrap a function turning it into a prop getter.

        Example:

            @y.prop("config.tool.name")
            def config_name(): pass

        """

        @wraps
        def getter_func(f):
            keys = value.split(".")
            parsed_value = None
            for key in keys:
                parsed_value = (
                    self.config[key] if parsed_value is None else parsed_value[key]
                )
            return parsed_value

        return getter_func

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def __contains__(self, key):
        return key in self.config

    def __len__(self):
        return len(self.config)

    def __repr__(self):
        return repr(self.config)
