import logging
import os
import platform
from threading import TIMEOUT_MAX

from apscheduler.schedulers.base import STATE_STOPPED
from apscheduler.schedulers.blocking import BlockingScheduler
from redis import Redis

PROCESS_KEY = f"{platform.node()}-{os.getpid()}"
CACHE_KEY = "schedule_leader"

logger = logging.getLogger("dramatiq_apscheduler")


class DummyExecutor:
    def submit_job(self, job, run_times):
        logger.debug(f"Skipping execution of {job.name}")


class RedisBlockingScheduler(BlockingScheduler):
    endpoint_url = None
    current_leader = False
    sticky_time = 280
    r = None

    def __init__(self, gconfig={}, endpoint_url="redis://localhost/", sticky_time=280, **options):
        self.endpoint_url = endpoint_url
        self.sticky_time = sticky_time
        super().__init__(gconfig, **options)

    def start(self, *args, **kwargs):
        self.r = Redis.from_url(self.endpoint_url)
        self.current_leader = self.check_current_leader()
        super().start(*args, **kwargs)

    def _main_loop(self):
        wait_seconds = TIMEOUT_MAX
        while self.state != STATE_STOPPED:
            self._event.wait(wait_seconds)
            self._event.clear()
            self.current_leader = self.check_current_leader()
            wait_seconds = self._process_jobs()

    def _lookup_executor(self, alias):
        """
        Checks if tasks should be added to queue and if not returns dummy executor
        """
        if self.current_leader:
            return super()._lookup_executor(alias)
        return DummyExecutor()

    def check_current_leader(self) -> bool:
        current_leader = self.r.get(CACHE_KEY)
        if current_leader is None:
            self.r.set(CACHE_KEY, PROCESS_KEY, 1)
            logger.debug(f"Set new leader to {PROCESS_KEY}")
            current_leader = self.r.get(CACHE_KEY)
        current_leader = current_leader.decode("utf-8")
        if current_leader == PROCESS_KEY:
            logger.debug(
                f"I am still the leader. Reserving for {self.sticky_time} more seconds"
            )
            self.r.expire(CACHE_KEY, self.sticky_time)
            return True
        ttl = self.r.ttl(CACHE_KEY)
        logger.debug(f"Current leader is {current_leader} with {ttl} seconds left")
        return False
