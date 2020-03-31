# -*- coding: utf-8 -*-
"""Configuration and fixtures for unit test suite."""
import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture
def run_cli_command():
    """Run a `click` command with the given options.

    The call will raise if the command triggered an exception or the exit code returned is non-zero
    """

    def _run_cli_command(command, options=None):
        """Run the command and check the result."""
        import traceback
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(command, options or [])

        assert result.exception is None, ''.join(traceback.format_exception(*result.exc_info))
        assert result.exit_code == 0, result.output

        return result

    return _run_cli_command
