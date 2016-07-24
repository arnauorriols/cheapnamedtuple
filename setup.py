import setuptools


setuptools.setup(name='cheapnamedtuple',
                 version="1.1.2",
                 description='Faster reimplementation of stdlib collections.namedtuple',
                 long_description=open('README.rst').read().strip(),
                 author='Arnau Orriols',
                 author_email='dev@arnauorriols.com',
                 url='https://github.com/arnauorriols/cheapnamedtuple',
                 py_modules=['cheapnamedtuple'],
                 license='MIT License',
                 keywords='namedtuple exec performance',
                 classifiers=['Intended Audience :: Developers',
                              'Programming Language :: Python :: 2 :: Only']
)
