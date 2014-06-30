from distutils.core import setup

setup(
    name='OozieConsole',
    version='0.1.0',
    author='Anbalagan Pugaleesan',
    author_email='anbu78@gmail.com',
    packages=['oozie'],
    scripts=['bin/ooziecli.py'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Oozie Console',
    long_description=open('README.txt').read(),
    install_requires=[
        "simplejson >= 2.3.0",
    ],
)
