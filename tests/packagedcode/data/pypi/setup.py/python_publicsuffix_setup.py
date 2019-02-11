#!/usr/bin/python

import os
import codecs
from setuptools import setup

def read_doc(name):
	return codecs.open(os.path.join(os.path.dirname(__file__), name), encoding='utf8').read()


def get_long_description():
	return read_doc("README.rst") + \
			"\n\nLicense\n-------\n\n" + \
			read_doc("LICENSE")

setup(name='publicsuffix',
	version='1.1.1',
	description='Get a public suffix for a domain name using the Public Suffix List.',
	license='MIT',
	long_description=get_long_description(),
	author='Tomaz Solc',
	author_email='tomaz.solc@tablix.org',

	packages = ['publicsuffix'],
	package_data = {
		'publicsuffix' : ['public_suffix_list.dat']
	},

	test_suite = 'tests',

	classifiers = [
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Topic :: Internet :: Name Service (DNS)",
	],
)
