import os
import shutil
import subprocess
import sys
from setuptools import setup
from setuptools.command.install import install

## manpage install code taken from https://github.com/novel/lc-tools
def abspath(path):
    """A method to determine absolute path
    for a relative path inside project's directory."""

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), path))

class fifo_install(install):

    def initialize_options(self):
        install.initialize_options(self)

    def run(self):
        install.run(self)
        man_dir = abspath("./doc/")

        output = subprocess.Popen([os.path.join(man_dir, "install.sh")],
                                  stdout=subprocess.PIPE,
                                  cwd=man_dir,
                                  env=dict({"PREFIX": self.prefix}, **dict(os.environ))).communicate()[0]
        print output

setup(
    name='PyFi',
    version='0.2.4',
    author='Heinz N. Gies',
    author_email='heinz@licenser.net',
    packages=['fifo', 'fifo.api'],
    scripts=['bin/fifo'],
    url='http://project-fifo.net',
    license='CDDL',
    description='Project FiFo API implementation and console client.',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    cmdclass={"install": fifo_install}
)
