from setuptools import setup

setup(
        name='Dataware Resource',
        version='1.0',
        packages=['prefstore'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
                "bottle == 0.11.4",
                "MySQL-python == 1.2.3",
                "gevent == 0.13.8",
        ]
)
