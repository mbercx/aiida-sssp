# -*- coding: utf-8 -*-
"""Commands to list instances of `SsspFamily`."""
import click
from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo

from . import options
from .root import cmd_root

PROJECTIONS_VALID = ('pk', 'uuid', 'label', 'description', 'count', 'version', 'functional', 'protocol')
PROJECTIONS_DEFAULT = ('label', 'version', 'functional', 'protocol', 'count')


def get_sssp_families_builder(version=None, functional=None, protocol=None):
    """Return a query builder that will query for SSSP families of the given configuration.

    :param version: optional version filter
    :param functional: optional functional filter
    :param protocol: optional protocol filter
    :return: `QueryBuilder` instance
    """
    from aiida.orm import QueryBuilder
    from aiida_sssp.groups import SsspFamily

    label = 'SSSP/{version}/{functional}/{protocol}'
    filters = {
        'label': {
            'like': label.format(version=version or '%', functional=functional or '%', protocol=protocol or '%')
        }
    }
    builder = QueryBuilder().append(SsspFamily, filters=filters)

    return builder


@cmd_root.command('list')
@options.VERSION(help='Filter for families with this version.')
@options.FUNCTIONAL(help='Filter for families with this functional.')
@options.PROTOCOL(help='Filter for families with this protocol.')
@options_core.PROJECT(type=click.Choice(PROJECTIONS_VALID), default=PROJECTIONS_DEFAULT)
@options_core.RAW()
@decorators.with_dbenv()
def cmd_list(version, functional, protocol, project, raw):
    """List installed configurations of the SSSP."""
    from tabulate import tabulate

    mapping_project = {
        'count': lambda family: family.count(),
        'version': lambda family: family.label.split('/')[1],
        'functional': lambda family: family.label.split('/')[2],
        'protocol': lambda family: family.label.split('/')[3],
    }

    rows = []

    for [group] in get_sssp_families_builder(version, functional, protocol).iterall():

        row = []

        for projection in project:
            try:
                projected = mapping_project[projection](group)
            except KeyError:
                projected = getattr(group, projection)
            row.append(projected)

        rows.append(row)

    if not rows:
        echo.echo_info('SSSP has not yet been installed: use `aiida-sssp install` to install it.')
        return

    if raw:
        echo.echo(tabulate(rows, disable_numparse=True, tablefmt='plain'))
    else:
        echo.echo(tabulate(rows, headers=[projection.capitalize() for projection in project], disable_numparse=True))
