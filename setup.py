import os
from setuptools import setup, find_packages

version = '0.0'

setup(name='potools',
      version=version,
      description="Python scripts to help with managing translations",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "changes.rst")).read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Wolfgang Thomas, Manuel Reinhardt, JC Brand',
      author_email='info@syslab.com',
      url='http://syslab.com',
      license='GPL',
      namespace_packages=['potools'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'sh',
          'polib',
          'mr.developer',
      ],
      extras_require={
          'podiff': ['polib', 'mr.developer'],
      },
      entry_points="""
      [console_scripts]
      podiff = potools.podiff:podiff
      """,
      )