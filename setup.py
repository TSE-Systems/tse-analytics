#!/usr/bin/env python

from subprocess import check_call

from setuptools import setup, find_packages, Command
from setuptools.command.sdist import sdist

install_requires = [
    'openpyxl'
    'pingouin',
    'PySide6',
    'psutil',
    'pyqtgraph',
    'tse-datatools',
]

dependency_links = [
]

cmdclass = {}


class custom_sdist(sdist):
    """Custom sdist command."""

    def run(self):
        self.run_command('build_res')
        sdist.run(self)


cmdclass['sdist'] = custom_sdist


class bdist_app(Command):
    """Custom command to build the application. """

    description = 'Build the application'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build_res')
        check_call(['pyinstaller', '-y', 'setup/tse-analytics.spec'])


cmdclass['bdist_app'] = bdist_app

setup(name='tse-analytics',
      version="0.1.0",
      packages=find_packages(),
      description='TSE Analytics',
      author='Anton Rau',
      author_email='anton.rau@tse-systems.com',
      license='MIT',
      url='https://github.com/TSE-Systems/tse-analytics',
      python_requires=">=3.10",
      install_requires=install_requires,
      dependency_links=dependency_links,
      entry_points={
          'gui_scripts': [
              'tse-analytics = tse_analytics.app:main'
          ]
      },
      cmdclass=cmdclass)
