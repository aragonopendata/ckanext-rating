import logging

import click

from ckanext.rating.commands import RatingCommand

log = logging.getLogger(__name__)


@click.group(short_help=u"Rating management commands.")
def rating():
    """Rating management commands.
    """
    pass


@rating.command()
def init():
    """Initialize the rating table.
    """
    log.info(u"Initialize the rating table.")
    cmd = RatingCommand()
    cmd.init_db()

def get_commands():
    return [rating]