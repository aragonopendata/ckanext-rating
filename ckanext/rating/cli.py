import click


@click.group(short_help=u"Rating management commands.")
def rating():
    """Rating management commands.
    """
    pass


def get_commands():
    return [rating]