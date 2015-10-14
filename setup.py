from ast import literal_eval
from setuptools import setup

def get_version(source='fsa4streams/__init__.py'):
    with open(source) as f:
        for line in f:
            if line.startswith('__version__'):
                return literal_eval(line.partition('=')[2].lstrip())
    raise ValueError("VERSION not found")

README = ''
with open('README.rst', 'r') as f:
    README = f.read()

setup(
    name='fsa4streams',
    version = get_version(),
    packages = ['fsa4streams'],
    description='An implementation of Finite State Automata for event streams',
    long_description = README,
    author='Pierre-Antoine Champin',
    #author_email='TODO',
    license='LGPL v3',
    #url='TODO',
    platforms='OS Independant',
    install_requires = [],
    tests_require = ["nose"],
    test_loader = 'nose.loader:TestLoader',
    test_suite='utests',
)