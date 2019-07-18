import sys
import logging
from traceback import format_tb

from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent, EVENT_JOB_EXECUTED
from apscheduler.executors.base import BaseExecutor
from dramatiq import Message
from dramatiq.broker import get_broker


class DramatiqExecutor(BaseExecutor):
    broker = None

    def __init__(self):
        super().__init__()
        self.broker = get_broker()
        logging.debug(f"Connected to dramatiq broker")

    def _do_submit_job(self, job, run_times):
        try:
            events = run_job(
                job, job._jobstore_alias, run_times, "dramatiq_apscheduler", self.broker
            )
        except BaseException:
            self._run_job_error(job.id, *sys.exc_info()[1:])
        else:
            self._run_job_success(job.id, events)


def run_job(job, jobstore_alias, run_times, logger_name, broker):
    logger = logging.getLogger(logger_name)
    events = []

    kwargs = dict(job.kwargs)
    func = kwargs.pop("func")
    queue_name = kwargs.pop("queue_name")

    for run_time in run_times:
        logger.info('Running job "%s" (scheduled at %s)', job, run_time)
        try:
            retval = broker.enqueue(
                Message(
                    queue_name=queue_name,
                    actor_name=func,
                    args=job.args,
                    kwargs=kwargs,
                    options={},
                )
            )
        except BaseException:
            exc, tb = sys.exc_info()[1:]
            formatted_tb = "".join(format_tb(tb))
            events.append(
                JobExecutionEvent(
                    EVENT_JOB_ERROR,
                    job.id,
                    jobstore_alias,
                    run_time,
                    exception=exc,
                    traceback=formatted_tb,
                )
            )
            logger.exception('Job "%s" raised an exception', job)

            import traceback

            traceback.clear_frames(tb)
            del tb
        else:
            events.append(
                JobExecutionEvent(
                    EVENT_JOB_EXECUTED, job.id, jobstore_alias, run_time, retval=retval
                )
            )
            logger.info('Job "%s" executed successfully', job)

    return events
