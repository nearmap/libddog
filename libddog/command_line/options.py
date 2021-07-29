import click


def attach_help_option(cmd: click.Command) -> click.Command:
    """
    Recursively attach -h/--help to every click Group and Command. Click by
    default only supports --help.
    """

    help = click.help_option("-h", "--help")

    if isinstance(cmd, click.Group):
        cmd.commands = {name: attach_help_option(c) for name, c in cmd.commands.items()}
        return help(cmd)

    elif isinstance(cmd, click.Command):
        return help(cmd)
