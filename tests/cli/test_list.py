# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-sssp list`."""
from aiida_sssp.cli import cmd_list
from aiida_sssp.cli.list import PROJECTIONS_VALID


def test_list(clear_db, run_cli_command, create_sssp_family):
    """Test the `aiida-sssp list` command."""
    result = run_cli_command(cmd_list)
    assert 'SSSP has not yet been installed: use `aiida-sssp install` to install it.' in result.output

    family = create_sssp_family()
    result = run_cli_command(cmd_list)

    assert family.label in result.output


def test_list_raw(clear_db, run_cli_command, create_sssp_family):
    """Test the `-r/--raw` option."""
    create_sssp_family()

    for option in ['-r', '--raw']:
        result = run_cli_command(cmd_list, [option])
        assert len(result.output_lines) == 1


def test_list_project(clear_db, run_cli_command, create_sssp_family):
    """Test the `-p/--project` option."""
    family = create_sssp_family()

    # Test that all `PROJECTIONS_VALID` can actually be projected and don't except
    for option in ['-P', '--project']:
        run_cli_command(cmd_list, [option] + list(PROJECTIONS_VALID))

    result = run_cli_command(cmd_list, ['--raw', '-P', 'label'])
    assert len(result.output_lines) == 1
    assert family.label in result.output


def test_list_filter(clear_db, run_cli_command, create_sssp_family):
    """Test the filtering options `--version`, `--functional` and `--protocol`."""
    create_sssp_family(label='SSSP/1.0/PBE/efficiency')
    create_sssp_family(label='SSSP/1.1/PBEsol/precision')

    result = run_cli_command(cmd_list, ['--raw'])
    assert len(result.output_lines) == 2

    for options in [
        ('--version', '1.0'),
        ('--version', '1.1'),
        ('--functional', 'PBE'),
        ('--functional', 'PBEsol'),
        ('--protocol', 'efficiency'),
        ('--protocol', 'precision'),
    ]:
        result = run_cli_command(cmd_list, ['--raw'] + list(options))
        assert len(result.output_lines) == 1
