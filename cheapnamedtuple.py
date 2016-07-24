from __future__ import print_function
from collections import Iterable, OrderedDict
from functools import partial
from keyword import iskeyword
from itertools import starmap
from operator import itemgetter
import sys

def namedtuple(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of tuple with named fields.
    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessible by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split()
    field_names = map(str, field_names)
    typename = str(typename)
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not all(c.isalnum() or c=='_' for c in name)
                or iskeyword(name)
                or not name
                or name[0].isdigit()
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    for name in [typename] + field_names:
        if type(name) != str:
            raise TypeError('Type names and field names must be strings')
        if not all(c.isalnum() or c=='_' for c in name):
            raise ValueError('Type names and field names can only contain '
                             'alphanumeric characters and underscores: {}'.format(name))
        if iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: {}'.format(name))
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with '
                             'a number: {}'.format(name))
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '{}'.format(name))
        if name in seen:
            raise ValueError('Encountered duplicate field name: {}'.format(name))
        seen.add(name)

    if verbose:
        print("Cheap means cheap...")

    field_names = tuple(field_names)
    arg_list = repr(tuple(field_names)).replace("'", "")[1:-1]

    class Namedtuple(tuple):
        __slots__ = ()
        _fields = tuple(field_names)

        def __new__(cls, *args, **kwargs):
            if len(args) == 1 and isinstance(args[0], Iterable):
                args = args[0]

            if len(args) > len(field_names):
                raise TypeError('Too many arguments')

            try:
                args = list(args) + [kwargs.pop(field)
                                     for field in field_names[len(args):]]
            except KeyError as e:
                raise TypeError('{} expects parameter {}'.format(typename, e))

            if kwargs:
                raise TypeError('{} got the unexpected '
                                'parameters {}'.format(typename, kwargs))

            return tuple.__new__(cls, args)

        __new__.__doc__ = \
            'Create new instance of {}({})'.format(typename, arg_list)

        def _make(cls, iterable, new=tuple.__new__, len=len):
            result = new(cls, iterable)
            if len(result) != len(field_names):
                raise TypeError(
                    'Expected {} arguments, '
                    'got {}'.format(len(field_names), len(result))
                )
            return result

        _make.__doc__ = (
            'Make a new {} object from a sequence '
            'or iterable'.format(typename)
        )

        # __doc__ of classmethods is read-only, need to wrap afterwards
        _make = classmethod(_make)

        def __repr__(self):
            'Return a nicely formatted representation string'
            return '{}({})'.format(
                typename,
                ', '.join(starmap('{}={}'.format, zip(self._fields, self)))
            )

        def _asdict(self):
            'Return a new OrderedDict which maps field names to their values'
            return OrderedDict(zip(self._fields, self))

        __dict__ = property(_asdict)

        def _replace(_self, **kwds):
            result = _self._make(map(kwds.pop, field_names, _self))
            if kwds:
                raise ValueError(
                    'Got unexpected field names: {}'.format(kwds.keys())
                )
            return result

        _replace.__doc__ = (
            'Return a new {typename} object replacing specified fields '
            'with new values'.format(typename=typename)
        )

        def __getnewargs__(self):
            'Return self as a plain tuple.  Used by copy and pickle.'
            return tuple(self)

        def __getstate__(self):
            'Exclude the OrderedDict from pickling'
            pass

        __doc__ = '{}({})'.format(typename, ', '.join(field_names))

    for index, field in enumerate(field_names):
        setattr(Namedtuple, field, property(itemgetter(index)))

    Namedtuple.__name__ = typename

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        Namedtuple.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return Namedtuple


class CheapNamedtuple(tuple):

    _fields = ()

    def __new__(cls, typename, field_names, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]

        if len(args) > len(field_names):
            raise TypeError('Too many arguments')

        try:
            args = list(args) + [kwargs.pop(field)
                                    for field in field_names[len(args):]]
        except KeyError as e:
            raise TypeError('{} expects parameter {}'.format(typename, e))

        if kwargs:
            raise TypeError('{} got the unexpected '
                            'parameters {}'.format(typename, kwargs))

        ntuple = tuple.__new__(cls, args)
        ntuple._fields = field_names
        ntuple._typename = typename
        return ntuple

    @classmethod
    def _make(cls, typename, fields, iterable, len=len):
        return cls(typename, fields, iterable)

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '{}({})'.format(
            self._typename,
            ', '.join(starmap('{}={}'.format, zip(self._fields, self)))
        )

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    __dict__ = property(_asdict)

    def _replace(self, **kwds):
        result = self._make(self._typename, self._fields,
                            map(kwds.pop, self._fields, self))
        if kwds:
            raise ValueError(
                'Got unexpected field names: {}'.format(kwds.keys())
            )
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return (self._typename, self._fields, tuple(self))

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        return (self._typename, self._fields)

    def __setstate__(self, state):
        self._typename, self._fields = state


    def __getattr__(self, name):
        if name in self._fields:
            return self[self._fields.index(name)]
        raise AttributeError(name)


def cheapnamedtuple(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of tuple with named fields.
    >>> Point = cheapnamedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessible by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split()
    field_names = tuple(map(str, field_names))
    typename = str(typename)

    adhoc_namedtuple = partial(CheapNamedtuple, typename, field_names)
    adhoc_namedtuple.__name__ = typename
    adhoc_namedtuple.__doc__ = '{}({})'.format(typename, ', '.join(field_names))
    adhoc_namedtuple._make = partial(adhoc_namedtuple.func._make,
                                     typename, field_names)
    adhoc_namedtuple._fields = field_names
    adhoc_namedtuple.__slots__ = ()
    try:
        adhoc_namedtuple.__module__ = \
            sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    adhoc_namedtuple.__getitem__ = adhoc_namedtuple.func.__getitem__
    return adhoc_namedtuple
