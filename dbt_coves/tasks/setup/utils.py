from rich.console import Console
from rich.table import Table

console = Console()

KEY_COLUMN_WIDTH = 50
VALUE_COLUMN_WIDTH = 30


def print_row(key, value="[green]FOUND :heavy_check_mark:[/green]", new_section=False):
    grid = Table.grid(expand=False)
    grid.add_column(width=KEY_COLUMN_WIDTH)
    grid.add_column(justify="right", width=VALUE_COLUMN_WIDTH)
    grid.add_row(key, value)
    if new_section:
        console.print("\n")
    console.print(grid)