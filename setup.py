from distutils.core import setup

setup(
    name='PyFi',
    version='0.1.0',
    author='Heinz N. Gies',
    author_email='heinz@licenser.net',
    packages=['fifo', 'fifo.api'],
    scripts=['bin/fifo'],
    url='http://project-fifo.net',
    license='LICENSE.txt',
    description='Project FiFo API implementation and console client.',
    long_description=open('README.md').read(),
)
