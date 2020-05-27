# -*- coding: utf-8 -*-
"""Commands to install a pseudo potential family."""
import os

import click

from aiida.cmdline.utils import decorators, echo

from .root import cmd_root
from .utils import attempt, create_family_from_archive
from . import options

URL_BASE = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/'


@cmd_root.command('install')
@options.VERSION(type=click.Choice(['1.0', '1.1']), default='1.1')
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol']), default='PBE')
@options.PROTOCOL(type=click.Choice(['efficiency', 'precision']), default='efficiency')
@click.option('-l', '--label', type=click.STRING,
    help='Label for the family, required when installing from an archive on the local file system.')
@click.option(
    '--archive',
    'filepath_archive',
    type=click.Path(exists=True),
    required=False,
    help='Install an SSSP configuration from this archive containing the pseudos instead of downloading it.'
)
@click.option(
    '--metadata',
    'filepath_metadata',
    type=click.Path(exists=True),
    required=False,
    help='Install an SSSP configuration using the metadata of this file instead of downloading it.'
)
@click.option('-t', '--traceback', is_flag=True, help='Include the stacktrace if an exception is encountered.')
@decorators.with_dbenv()
def cmd_install(version, functional, protocol, label, traceback, filepath_archive, filepath_metadata):
    """Install a configuration of the SSSP.

    The SSSP configuration will be automatically downloaded from the Materials Cloud Archive entry to create a new
    `SsspFamily`. It is possible to install a pseudo potential family from an archive on the local file system, but in
    that case a normal `UpfFamily` will be created, because the contents of the pseudopotentials cannot be validated to
    correspond to a valid SSSP configuration.
    """
    # pylint: disable=too-many-locals,too-many-arguments
    import requests
    import tempfile

    from aiida.common import exceptions
    from aiida.common.files import md5_file
    from aiida.orm import QueryBuilder

    from aiida_sssp import __version__
    from aiida_sssp.groups import SsspConfiguration, SsspFamily, UpfFamily

    if filepath_archive or filepath_metadata:
        cls = UpfFamily
        if label is None:
            raise click.BadParameter('defining a label is required when installing from disk', param_hint='`--label`')
        description = None
    else:
        cls = SsspFamily
        label = '{}/{}/{}/{}'.format('SSSP', version, functional, protocol)
        description = 'SSSP v{} {} {} installed with aiida-sssp v{}'.format(version, functional, protocol, __version__)
        url_base = '{}/SSSP_{}_{}_{}'.format(URL_BASE, version, functional, protocol)
        configuration = SsspConfiguration(version, functional, protocol)

        if configuration not in SsspFamily.valid_configurations:
            echo.echo_critical('{} {} {} is not a valid SSSP configuration'.format(*configuration))

    try:
        QueryBuilder().append(cls, filters={'label': label}).limit(1).one()
    except exceptions.NotExistent:
        pass
    else:
        echo.echo_critical('{}<{}> is already installed'.format(cls.__name__, label))

    with tempfile.TemporaryDirectory() as dirpath:

        if not filepath_archive or not filepath_metadata:
            url_archive = url_base + '.tar.gz'
            filepath_archive = os.path.join(dirpath, 'archive.tar.gz')

            with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
                response = requests.get(url_archive)
                response.raise_for_status()
                with open(filepath_archive, 'wb') as handle:
                    handle.write(response.content)
                    handle.flush()
                    description += '\nArchive pseudos md5: {}'.format(md5_file(filepath_archive))

        if not filepath_archive or not filepath_metadata:
            url_metadata = url_base + '.json'
            filepath_metadata = os.path.join(dirpath, 'metadata.json')

            with attempt('downloading selected pseudo potentials metadata... ', include_traceback=traceback):
                response = requests.get(url_metadata)
                response.raise_for_status()
                with open(filepath_metadata, 'wb') as handle:
                    handle.write(response.content)
                    handle.flush()
                    description += '\nPseudo metadata md5: {}'.format(md5_file(filepath_metadata))

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(cls, label, filepath_archive, filepath_metadata)

        family.description = description
        echo.echo_success('installed `{}` containing {} pseudo potentials'.format(label, family.count()))
