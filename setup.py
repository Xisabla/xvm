from setuptools import setup

setup(
    name='xvm',
    description='Quick, dirty and very not complete implementation of a CLI for VirtualBox',
    version='0.0.1',
    install_requires=[
        'typer',
    ],
    packages=['xvm'],
    entry_points={
        'console_scripts': [
            'xvm = xvm.cli:app',
        ],
    },
)
