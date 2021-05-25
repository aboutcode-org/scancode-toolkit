# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='PyJPString',
    version='0.0.3',
    description='Python japanese string utilities.',
    author='odoku',
    author_email='masashi.onogawa@wamw.jp',
    keywords='japanese,string',
    url='http://github.com/odoku/PyJPString',
    license='MIT',

    packages=[
        'jpstring',
        'jpstring.django',
    ],
    install_requires=[
        'six>=1.10.0',
        'zenhan>=0.5.2',
    ],
    extras_require={
        'test': [
            'django',
            'pytest==2.9.1',
        ],
    }
)
