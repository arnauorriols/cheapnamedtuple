Cheap namedtuple implementation (Python 2.7)
============================================

Namedtuples are a neat goody of Python, but they have one big caveat. In order to be
precise with the type definition, they compile with exec a string template, formated
with the variables given in the namedtuple() function factory. This compilation is very
expensive computation-wise, and in practice can be spared if needed for performance reasons.

An [issue](http://bugs.python.org/issue3974) was opened years ago in the Python bug tracker
but it got rejected, arguing that the official implementation is clearer and 
more maintainable. This is true, but there are cases where performance is key, and the current
implementation using exec is just not an option.

If you need to define new namedtuple types dynamically, and you have high performance constraints,
this is for you.

There are multiple versions out there, using [metaclasses](https://gist.github.com/aliles/1160525),
or [metaclasses](http://bugs.python.org/file11608/new_namedtuples.diff), or [ABC](http://code.activestate.com/recipes/577629-namedtupleabc-abstract-base-class-mix-in-for-named/)

This versions is simpler. Just define a new class closed-over by the factory function.

Unittests from cPython2.7 implementation are copied here to assert that the same expected behaviour is honored. 

Install
-------

    pip install cheapnamedtuple

Usage
-----

    >>> from cheapnamedtuple import namedtuple
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

Compatibility
=============

Currently only tested in Python 2.7

Benchmarking
============

    $ python -m timeit -vvvv "from cheapnamedtuple import namedtuple" "A = namedtuple('A', ['foo', 'bar', 'foobar'])" "a = A(1, 2, 3)" "a.bar"
    10 loops -> 0.00332594 secs
    100 loops -> 0.01106 secs
    1000 loops -> 0.09164 secs
    10000 loops -> 0.955008 secs
    raw times: 0.929455 0.872804 0.904877
    10000 loops, best of 3: 87.2804 usec per loop

    $python -m timeit -vvvv "from collections import namedtuple" "A = namedtuple('A', ['foo', 'bar', 'foobar'])" "a = A(1, 2, 3)" "a.bar" 
    10 loops -> 0.00922394 secs
    100 loops -> 0.0595999 secs
    1000 loops -> 0.350676 secs
    raw times: 0.328964 0.33169 0.327519
    1000 loops, best of 3: 327.519 usec per loop

Using metaclass version found [here](https://gist.github.com/aliles/1160525):

    $ python -m timeit -vvvv "from metanamedtuple import namedtuple" "A = namedtuple('A', ['foo', 'bar', 'foobar'])" "a = A(1, 2, 3)" "a.bar" 
    10 loops -> 0.00334907 secs
    100 loops -> 0.0108609 secs
    1000 loops -> 0.088969 secs
    10000 loops -> 1.25756 secs
    raw times: 1.2868 1.24004 1.25383
    10000 loops, best of 3: 124.004 usec per loop
