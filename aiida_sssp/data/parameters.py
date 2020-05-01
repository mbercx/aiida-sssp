# -*- coding: utf-8 -*-
"""Subclass of `Data` to represent metadata parameters for a specific `SsspFamily`."""
from aiida import orm
from aiida.common.lang import type_check

__all__ = ('SsspParameters',)


class SsspParameters(orm.Data):
    """Subclass of `Data` to represent metadata parameters for a specific `SsspFamily`."""

    KEY_FAMILY_LABEL = 'family_label'

    def __init__(self, parameters, label, **kwargs):
        """Construct a new instance of metadata parameters for an `SsspFamily`.

        .. note:: the direction of control flows from the `SsspFamily` to the `SsspParameters`. That is to say, the
            parameters only "knows" about the `SsspFamily` through the `family_label` that should correspond to the
            label of the `SsspFamily`. However, the responsibility of validating the correspondence of the parameters
            metadata and the actual pseudos contained in the `SsspFamily` is up to the family. The `SsspParameters` will
            only guarantee that for each element that it specifies, the format of the metadata is complete and of the
            correct type. It will not validate the actual values.

        :param parameters: metadata parameters of a given `SsspFamily`. Should be a dictionary of elements, where each
            element provides a dictionary of `cutoff_wfc`, `cutoff_rho`, `filename` and `md5`.
        :param label: the label of the family to which this parameters should be coupled.
        """
        super().__init__(**kwargs)

        type_check(parameters, dict)
        type_check(label, str)

        for element, values in parameters.items():
            for key, valid_types in [('filename', str), ('md5', str), ('cutoff_wfc', float), ('cutoff_rho', float)]:
                try:
                    type_check(values[key], valid_types)
                except KeyError:
                    raise ValueError('entry for element `{}` is missing the `{}` key'.format(element, key))
                except TypeError:
                    raise ValueError('`{}` for element `{}` is not of type {}'.format(key, element, valid_types))

        self.set_attribute_many(parameters)
        self.family_label = label

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

    def get_metadata(self, element=None):
        """Return the metadata for all or a specific element.

        :param element: optional element
        :raises KeyError: if the element is not defined for this instance
        """
        if element is None:
            metadata = dict(self.attributes)
            metadata.pop(self.KEY_FAMILY_LABEL)
            return metadata

        try:
            return self.get_attribute(element)
        except AttributeError:
            raise KeyError('element `{}` is not defined for `{}`'.format(element, self))
