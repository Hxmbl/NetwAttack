# entry point of the program

import os
from src.modules.passbrute.core import passbrute
import time
import pathlib
import typer

app = typer.Typer()

@app.command()
def main(mode: str):
    if mode == "passbrute":
        typer.echo("Going to passbrute mode...")
        passbrute()
    elif mode == "randomshitnotdevidedyet":
        typer.echo("You never saw this.")
        exit()
    else:
        typer.echo(typer.style("Use --help flag if you don't know what you're doing", fg=typer.colors.RED))

if __name__ == "__main__":
    app()