import click
from comtacts.comtacts import add_port, get_port, all_contacts, _get_storage_dir

@click.group()
def cli():
    """Manage COM port contacts"""
    pass

@cli.command()
@click.option('--name', required=True, help='Name for this contact')
@click.option('--port', required=True, help='Current COM port (e.g., COM3)')
@click.option('--overwrite', is_flag=True, help='Overwrite an existing contact with the same name')
def add(name, port, overwrite):
    """Add a new contact"""
    try:
        add_port(name, port, overwrite)
        click.echo(f"Added contact '{name}' for port {port}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
@click.option('--name', required=True, help='Name of the contact')
def get(name):
    """Get port for a contact"""
    try:
        port = get_port(name)
        click.echo(port)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
def all():
    """List all contacts"""
    try:
        contacts = all_contacts()
        if len(contacts) == 0:
            click.echo("No contacts found")
        else:
            for name in contacts:
                click.echo(name)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
def where():
    """Show where contacts are being stored"""
    try:
        click.echo(_get_storage_dir())
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

if __name__ == "__main__":
    cli()