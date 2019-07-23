import os
import platform
import click
import redis
import redis_lock
import yaml
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from click import ClickException
from dramatiq import set_broker, get_broker, Message
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from pytz import utc

from apscheduler.triggers.cron import CronTrigger

PROCESS_KEY = f"{platform.node()}-{os.getpid()}"
LOCK_NAME = "schedule_leader"

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)-5.5s] {PROCESS_KEY} %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

logging.getLogger("pika").setLevel(logging.CRITICAL)


def enqueue_dramatiq_job(**message):
    broker = get_broker()
    broker.enqueue(Message(**message))


def add_all_jobs(scheduler, jobs):
    for name, options in jobs.items():
        trigger = CronTrigger.from_crontab(options["crontab"])

        scheduler.add_job(
            id=name,
            name=name,
            func=enqueue_dramatiq_job,
            kwargs={
                "queue_name": options.get("queue_name", "default"),
                "actor_name": options["func"],
                "args": options.get("args", []),
                "kwargs": options.get("kwargs", {}),
                "options": {"max_retries": 0}
            },
            trigger=trigger,
            replace_existing=True,
        )


@click.command()
@click.argument("task_file", type=click.File("r"))
@click.option("--debug", is_flag=True, help="Enables debug logging")
@click.option(
    "--rabbitmq", default=None, help="rabbitmq connection url: amqp://127.0.0.1:5672/"
)
@click.option(
    "--redis_url",
    default="redis://localhost/",
    help="redis connection url: redis://localhost/",
)
@click.option(
    "--expire", default=60, type=int, help="How long the lock should last for"
)
def schedule(task_file, debug, rabbitmq, redis_url, expire):
    try:
        config = yaml.safe_load(task_file)
    except yaml.YAMLError as e:
        raise ClickException(f"Yaml task file is invalid: {e}")

    if rabbitmq:
        rabbitmq_broker = RabbitmqBroker(url=rabbitmq)
        set_broker(rabbitmq_broker)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("pika").setLevel(logging.CRITICAL)

    scheduler = BlockingScheduler(timezone=utc)
    try:
        add_all_jobs(scheduler, config["jobs"])
    except KeyError as e:
        raise ClickException(f"Config file missing required parameter: {e.args}")

    conn = redis.Redis.from_url(redis_url)
    with redis_lock.Lock(conn, LOCK_NAME, id=PROCESS_KEY, expire=expire, auto_renewal=True):
        scheduler.start()


def cli():
    schedule(auto_envvar_prefix="SCHEDULE")
