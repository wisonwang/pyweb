# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name = 'IceMongo'
version = '0.0.1'
author = 'WisonWang'
author_email = 'fangfu2012@gmail.com'
license = 'MIT'

setup(name=name,
      packages=find_packages(),
      version=version,
      description=u"IceMongo是一个基于Zeroc和MongoDB 的分布式服务框架",
      author=author,
      author_email=author_email,
      license=license,
      url='https://github.com/wisonwang/icemongo')
