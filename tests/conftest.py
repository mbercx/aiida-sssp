# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Configuration and fixtures for unit test suite."""
import os
import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture
def clear_db(clear_database_before_test):
    """Alias for the `clear_database_before_test` fixture from `aiida-core`."""
    yield


@pytest.fixture
def run_cli_command():
    """Run a `click` command with the given options.

    The call will raise if the command triggered an exception or the exit code returned is non-zero
    """

    def _run_cli_command(command, options=None, raises=None):
        """Run the command and check the result.

        :param options: the list of command line options to pass to the command invocation
        :param raises: optionally an exception class that is expected to be raised
        """
        import traceback
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(command, options or [])

        if raises is not None:
            assert result.exception is not None, result.output
            assert result.exit_code != 0
        else:
            assert result.exception is None, ''.join(traceback.format_exception(*result.exc_info))
            assert result.exit_code == 0, result.output

        result.output_lines = [line.strip() for line in result.output.split('\n') if line.strip()]

        return result

    return _run_cli_command


@pytest.fixture
def filepath_fixtures():
    """Return the absolute filepath to the directory containing the file `fixtures`."""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def filepath_pseudos(filepath_fixtures):
    """Return the absolute filepath to the directory containing the pseudo potential files."""
    return os.path.join(filepath_fixtures, 'pseudos')


@pytest.fixture
def get_upf_data(filepath_pseudos):
    """Return `UpfData` for a given element."""

    def _get_upf_data(element='He'):
        from aiida.plugins import DataFactory
        UpfData = DataFactory('upf')
        return UpfData(os.path.join(filepath_pseudos, '{}.upf'.format(element)))

    return _get_upf_data


@pytest.fixture
def create_sssp_family(filepath_pseudos):
    """Create an `SsspFamily` from the `tests/fixtures/pseudos` directory."""

    def factory(label='SSSP/1.1/PBE/efficiency', description='SSSP v1.1 PBE efficiency'):
        from aiida_sssp.groups import SsspFamily
        return SsspFamily.create_from_folder(filepath_pseudos, label, description)

    return factory


@pytest.fixture
def create_sssp_parameters(create_sssp_family):
    """Create an `SsspParameters` from the `tests/fixtures/pseudos` directory."""

    def factory(family=None, parameters=None):
        from aiida_sssp.data import SsspParameters

        if family is None:
            family = create_sssp_family()

        if parameters is None:
            parameters = {
                'Ar': {
                    'cutoff_wfc': 10.,
                    'cutoff_rho': 20.,
                    'filename': 'Ar.upf',
                    'md5': '91d02ab07c14fb60c3c6496920ee6523'
                },
                'He': {
                    'cutoff_wfc': 20.,
                    'cutoff_rho': 80.,
                    'filename': 'He.upf',
                    'md5': '202f5b754e21ed83f3bbcc5255632b0e'
                },
                'Ne': {
                    'cutoff_wfc': 30.,
                    'cutoff_rho': 240.,
                    'filename': 'Ne.upf',
                    'md5': '778fbbd85300b29561a271270126513b'
                }
            }

        return SsspParameters(family, parameters)

    return factory
