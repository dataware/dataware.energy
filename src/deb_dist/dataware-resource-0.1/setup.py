from setuptools import setup

setup(
    name='dataware-resource',
    version='0.1',
    packages=['dataware'],
    scripts=['dataware-energy'],
    license='MIT license',
    long_description=open('README.txt').read(),
    include_package_data=True,
)
