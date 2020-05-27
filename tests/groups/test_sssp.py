# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `SsspFamily` class."""
import pytest

from aiida_sssp.groups import SsspConfiguration, SsspFamily


def test_default_configuration():
    """Test the `SsspFamily.default_configuration` class attribute."""
    assert isinstance(SsspFamily.default_configuration, SsspConfiguration)


def test_valid_configurations():
    """Test the `SsspFamily.valid_configurations` class attribute."""
    valid_configurations = SsspFamily.valid_configurations
    assert isinstance(valid_configurations, tuple)

    for entry in valid_configurations:
        assert isinstance(entry, SsspConfiguration)


def test_get_valid_labels():
    """Test the `SsspFamily.get_valid_labels` class method."""
    valid_labels = SsspFamily.get_valid_labels()
    assert isinstance(valid_labels, tuple)

    for entry in valid_labels:
        assert isinstance(entry, str)


def test_format_configuration_label():
    """Test the `SsspFamily.format_configuration_label` class method."""
    configuration = SsspConfiguration(1.1, 'PBE', 'efficiency')
    assert SsspFamily.format_configuration_label(configuration) == 'SSSP/1.1/PBE/efficiency'


def test_constructor():
    """Test that the `SsspFamily` constructor validates the label."""
    with pytest.raises(ValueError, match=r'the label `.*` is not a valid SSSP configuration label'):
        SsspFamily()

    with pytest.raises(ValueError, match=r'the label `.*` is not a valid SSSP configuration label'):
        SsspFamily(label='SSSP_1.1_PBE_efficiency')

    label = SsspFamily.format_configuration_label(SsspFamily.default_configuration)
    family = SsspFamily(label=label)
    assert isinstance(family, SsspFamily)