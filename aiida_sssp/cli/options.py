# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import click

from aiida.cmdline.params.options import OverridableOption

__all__ = ('VERSION', 'FUNCTIONAL', 'PROTOCOL')

VERSION = OverridableOption(
    '-v', '--version', type=click.STRING, required=False, help='Select the version of the SSSP configuration.'
)

FUNCTIONAL = OverridableOption(
    '-f', '--functional', type=click.STRING, required=False, help='Select the functional of the SSSP configuration.'
)

PROTOCOL = OverridableOption(
    '-p', '--protocol', type=click.STRING, required=False, help='Select the protocol of the SSSP configuration.'
)
