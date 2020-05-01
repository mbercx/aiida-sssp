# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-sssp install`."""
from aiida import orm
from aiida_sssp.cli import cmd_install


def test_install(clear_db, run_cli_command):
    """Test the `aiida-sssp install` command."""
    from aiida_sssp.groups import SsspFamily

    result = run_cli_command(cmd_install)
    assert 'installed `SSSP/' in result.output
    assert orm.QueryBuilder().append(SsspFamily).count() == 1

    result = run_cli_command(cmd_install, raises=SystemExit)
    assert 'is already installed' in result.output
