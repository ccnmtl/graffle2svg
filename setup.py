from setuptools import setup, find_packages
import sys, os

try:
    import py2exe
except:
    pass

version = '0.3'

setup(name='graffle2svg',
      version=version,
      description="Basic converter from omnigraffle to svg",
      long_description="""\
Convert omnigraffle files to svg images""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='svg graffle converter convert',
      author='Tim Wintle',
      author_email='tim.wintle@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=["graffle2svg/scripts/graffle2svg","graffle2svg/scripts/graffle2svgview"],
      console=["graffle2svg/scripts/graffle2svg","graffle2svg/scripts/graffle2svgview"] #py2exe
      )
