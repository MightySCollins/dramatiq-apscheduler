import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='dramatiq-apscheduler',
    version='0.3',
    packages=find_packages(),
    py_modules=['dramatiq_apscheduler'],
    author="Sam Collins",
    url="https://github.com/MightySCollins/dramatiq-apscheduler/",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    license="MIT",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=[
        'Click',
        'pyyaml',
        'apscheduler',
        'dramatiq',
        'pytz',
        'pika',
        'redis'
    ],
    entry_points='''
        [console_scripts]
        dramatiq_apscheduler=dramatiq_apscheduler.main:cli
    ''',
)