from pathlib import Path
from typing import Any, Dict, Union

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader


def render_template_file(
    name,
    context: Dict[str, Any],
    output_path: Union[str, Path],
    templates_folder: str = ".dbt_coves/templates",
) -> str:
    env = Environment(
        loader=ChoiceLoader(
            [FileSystemLoader(templates_folder), PackageLoader("dbt_coves")]
        ),
        keep_trailing_newline=True,
    )
    template = env.get_template(name)
    output = template.render(**context)

    with open(output_path, "w") as rendered:
        rendered.write(output)

    return output


def render_template(template_content: str, context: Dict[str, Any]):
    return Environment().from_string(template_content).render(**context)
