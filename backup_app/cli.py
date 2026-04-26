import typer
from .services.commands import commands

app = typer.Typer(invoke_without_command=True)

@app.callback()
def main(ctx: typer.Context):
    # If no subcommand was invoked
    if ctx.invoked_subcommand is None:
        commands.run_backup()

@app.command("run")
def run(dry_run: bool = typer.Option(False, '--dry-run', help='Simulate backup without copying files')):
    #get_command('run-backup', dry_run=dry_run)
    commands.run_backup(dry_run=dry_run)

@app.command("add-source")
def add_source(path: str):
    commands.add_source(path)
    print(f'successfully filled in {path}')

@app.command("get-sources")
def list_sources():
    for i, src in enumerate(commands.get_sources(), start=1):
        print(f'{i} : {src}')

@app.command('pop-source')
def pop_path(idx: int):
    if not idx:
        print('invalid index')
        return
    sources = commands.get_sources()
    try:
        removed = sources[idx -1] # Get the actual path
    except IndexError:
        print('Index out of range')
        return
    commands.rem_source(idx -1)
    print(f'Successfully removed {removed}')
    
@app.command('swap-default')
def swap_default(path: str):
    if not path:
        print('Please include a path')
        return
    commands.change_default(path)

@app.command('swap-backup')
def swap_backup(path: str):
    if not path:
        print('Not a valid path included')
        return
    commands.change_backup(path)

@app.command('get-backup')
def get_backup():
    print(commands.get_backup())
    
@app.command('get-default')
def get_default():
    print(commands.get_default())
    