# -*- coding: utf-8 -*-
"""Subclass of `Data` to represent parameters for a specific `SsspFamily`."""
from aiida import orm
from aiida.common.lang import type_check

__all__ = ('SsspParameters',)


class SsspParameters(orm.Data):
    """Subclass of `Data` to represent parameters for a specific `SsspFamily`."""

    KEY_FAMILY_LABEL = 'family_label'

    def __init__(self, family, parameters, **kwargs):
        """Construct a new instance of cutoff parameters for an `SsspFamily`.

        The family has to an instance of `SsspFamily`. The `parameters` should be a dictionary of elements, where each
        element provides a dictionary of `cutoff_wfc`, `cutoff_rho`, `filename` and `md5`.

        :param parameters: the dictionary with parameters of a given `SsspFamily`
        :param family: an instance of `SsspFamily` to which the parameters should apply.
        """
        from aiida_sssp.groups import SsspFamily
        super().__init__(**kwargs)

        type_check(parameters, dict)
        type_check(family, SsspFamily, msg='`family` is not an instance of `SsspFamily`')

        for element, values in parameters.items():
            for key, valid_types in [('filename', str), ('md5', str), ('cutoff_wfc', float), ('cutoff_rho', float)]:
                try:
                    type_check(values[key], valid_types)
                except KeyError:
                    raise ValueError('entry for element `{}` is missing the `{}` key'.format(element, key))
                except TypeError:
                    raise ValueError('`{}` for element `{}` is not of type {}'.format(key, element, valid_types))

        self.set_attribute_many(parameters)
        self.set_attribute(self.KEY_FAMILY_LABEL, family.label)

    def __repr__(self):
        """Represent the instance for debugging purposes."""
        return '{}<{}>'.format(self.__class__.__name__, self.pk or self.uuid)

    def __str__(self):
        """Represent the instance for human-readable purposes."""
        return self.__repr__()

    @property
    def family_label(self):
        """Return the label of the `SsspFamily` to which this parameters instance is associated.

        :return: the label of the associated `SsspFamily`
        """
        return self.get_attribute(self.KEY_FAMILY_LABEL)

    @family_label.setter
    def family_label(self, value):
        """Set the label of the `SsspFamily` to which this parameters instance is associated.

        :param value: the label of the associated `SsspFamily`
        :raises: `~aiida.common.exceptions.ModificationNotAllowed`
        """
        return self.set_attribute(self.KEY_FAMILY_LABEL, value)

    @property
    def elements(self):
        """Return the set of elements defined for this instance.

        :return: set of elements
        """
        return set(self.attributes_keys()) - {self.KEY_FAMILY_LABEL}

    def get_metadata(self, element):
        """Return the metadata for the given element.

        :raises KeyError: if the element is not defined for this instance
        """
        try:
            return self.get_attribute(element)
        except AttributeError:
            raise KeyError('element `{}` is not defined for `{}`'.format(element, self))
