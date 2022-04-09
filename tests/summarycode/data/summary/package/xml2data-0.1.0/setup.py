# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='xml2data',
      version=version,
      description="a library for converting xml into native data",
      long_description=u'''\
xml2data is a library for converting xml into native data, according to css-selector like template.

Requirements
------------

Python 2.7

Example
-------

the following converts `a webpage <http://hp.vector.co.jp/authors/VA038583/>`_ containing some app information::

  import xml2data
  template = """{
    'apps': [div#main-container div.section:first-child div.goods-container div.goods @ {
        'name': div.top span.name,
        'url': div.top span.name a $[href],
        'description': div.goods div.bottom
    }],
    'author': div#main-container div.section div.text p a:first-child $text,
    'twitter': div#main-container div.section div.text p a:nth-child(2) $[href]
  }"""
  data = xml2data.urlload('http://hp.vector.co.jp/authors/VA038583/', template)

results::

  data == {
    'apps': [{
        'name': 'copipex',
        'url': './down/copipex023.zip',
        'description': '<コピー⇒貼付け> が <マウスで範囲選択⇒クリック> で可能に'
      }, {
        'name': 'gummi',
        'url': './gummi.html', 
        'description': 'ウィンドウの任意の部分を別窓に表示。操作も可能'
      }, {
        'name': 'PAWSE',
        'url': './down/pawse032.zip',
        'description': 'Pauseキーで、アプリケーションの一時停止、実行速度の制限が可能に'
      }, {
        'name': 'onAir',
        'url': './onair.html',
        'description': '現在放送中のテレビ番組のタイトルを一覧表示'
      }],
    'author': 'slay', 
    'twitter': 'http://twitter.com/slaypni'
  }
      ''',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Markup :: HTML',
          'Topic :: Text Processing :: Markup :: XML'
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='xml html',
      author='slaypni',
      url='https://github.com/slaypni/xml2data',
      license='MIT',
      packages=find_packages(exclude=['xml2data.testsuite']),
      test_suite='xml2data.testsuite.suite',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'lxml',
          'cssselect',
          'chardet',
          'minimock'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
