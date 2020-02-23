import os
from setuptools import setup

setup(
    name='ltl',
    author=u'Baruch Sterin',
    author_email='ltl@bsterin.com',
    version='0.0.1',
    packages=[
        'ltl'
    ],
    install_requires=[
        'ply',
        'pyaig',
        'future',
        'click'
    ],
    entry_points={
        "console_scripts": [
            "ltl = ltl.__main__:main"
        ]
    }
)
