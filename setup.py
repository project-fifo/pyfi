from distutils.core import setup

setup(
    name='PyFi',
    version='0.1.3',
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
)
