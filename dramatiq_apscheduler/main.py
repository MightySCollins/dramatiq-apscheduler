import os
import platform
import click
import yaml
import logging

from click import ClickException
from pytz import utc

from apscheduler.triggers.cron import CronTrigger

from dramatiq_apscheduler.executor import DramatiqExecutor
from dramatiq_apscheduler.scheduler import RedisBlockingScheduler

PROCESS_KEY = f"{platform.node()}-{os.getpid()}"

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)-5.5s] {PROCESS_KEY}  %(message)s",
    handlers=[
        logging.StreamHandler()
    ])

logging.getLogger("pika").setLevel(logging.CRITICAL)

logger = logging.getLogger("dramatiq_apscheduler")


def dummy_job(**kwargs):
    return


def add_all_jobs(scheduler, jobs, grace_time=280):
    for name, options in jobs.items():
        if "crontab" in options:
            trigger = CronTrigger.from_crontab(options["crontab"])
        else:
            logger.warning(f"No trigger specified for {name}. Task will run immediatly")
            trigger = None

        try:
            kwargs = options.get("kwargs", {})
            kwargs["func"] = options["func"]
            kwargs["queue_name"] = options.get("queue_name", "default")
        except KeyError:
            raise ClickException("Config file missing required paramter")

        scheduler.add_job(
            id=name,
            name=name,
            func=dummy_job,
            kwargs=kwargs,
            trigger=trigger,
            replace_existing=True,
        )


@click.command()
@click.argument('configfile', type=click.File('r'))
@click.option('--debug', is_flag=True)
def schedule(configfile, debug):
    try:
        config = yaml.safe_load(configfile)
    except yaml.YAMLError as e:
        raise ClickException(f"Yaml config file is invalid: {e}")

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
        logging.getLogger("apscheduler").setLevel(logging.DEBUG)

    executors = {
        'default': DramatiqExecutor()
    }
    scheduler = RedisBlockingScheduler(executors=executors, timezone=utc)
    add_all_jobs(scheduler, config['jobs'])
    scheduler.start()
