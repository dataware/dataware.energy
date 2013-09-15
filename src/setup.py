from setuptools import setup

setup(
    name='dataware-energy',
    version='0.1',
    packages=['dataware-energy'],
    scripts=['dataware_energy','currentcost-monitor', 'currentcost-stop'],
    license='MIT license',
    long_description=open('README.txt').read(),
    include_package_data=True,
)
