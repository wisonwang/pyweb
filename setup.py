# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name = 'pyweb'
version = '0.0.1'
author = 'WisonWang'
author_email = 'fangfu2012@gmail.com'
license = 'MIT'

setup(name=name,
      packages=find_packages(),
      version=version,
      description=u"python tornado + protocol buffer + mongo web framework",
      author=author,
      author_email=author_email,
      license=license,
      url='https://github.com/wisonwang/pyweb')
