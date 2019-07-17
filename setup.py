from setuptools import setup

setup(
    name='dramatiq-apscheduler',
    version='0.1',
    py_modules=['dramatiq_apscheduler'],
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
        dramatiq_apscheduler=dramatiq_apscheduler.main:schedule
    ''',
)