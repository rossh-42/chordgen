from setuptools import find_packages
from setuptools import setup


def get_global(file_name, global_name):
    """Read global_name from file."""
    import os
    globals = {}
    exec(open(os.path.join(os.path.dirname(__file__), "mellowchord", file_name)).read(), globals)
    return globals[global_name]


setup(
    name=get_global("version.py", "__title__"),
    version=get_global("version.py", "__version__"),
    install_requires=['mido',
                      'musthe',
                      'networkx',
                      'python-rtmidi',
                      'readchar'],
    description=get_global("version.py", "__description__"),
    long_description=get_global("version.py", "__description__"),
    author=get_global("version.py", "__author__"),
    author_email=get_global("version.py", "__author_email__"),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mc=mellowchord:main',
            'mellowchord=mellowchord:main',
        ],
    },
)
