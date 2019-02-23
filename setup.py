#!/usr/bin/env python

import os
from setuptools import setup

with open('flowws/version.py') as version_file:
    exec(version_file.read())

setup(name='flowws',
      author='Matthew Spellings',
      author_email='matthew.p.spellings@gmail.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
      ],
      description='Library for development of stage-based scientific workflows',
      entry_points={
          'console_scripts': [
              'flowws_run = flowws:Workflow.run_from_command',
          ],
      },
      extras_require={},
      install_requires=[],
      license='BSD',
      packages=[
          'flowws',
      ],
      python_requires='>=3',
      version=__version__
      )
