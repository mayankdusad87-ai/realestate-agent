"""
Task scheduling for automated agent runs.

Wraps APScheduler to provide pre-defined schedules (daily, weekly, monthly)
aligned to IST business hours for the real estate domain.
"""
import logging
from collections.abc import Callable
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_TIMEZONE = "Asia/Kolkata"


class Schedule(Enum):
    """Pre-defined cron schedules for agent jobs."""

    DAILY_EVENING = "daily_evening"  # 7 PM IST
    WEEKLY_MONDAY = "weekly_monday"  # Monday 9 AM IST
    WEEKLY_FRIDAY = "weekly_friday"  # Friday 5 PM IST
    MONTHLY_FIRST = "monthly_first"  # 1st of month 10 AM IST


_SCHEDULE_CRONS: dict[Schedule, dict] = {
    Schedule.DAILY_EVENING: {"hour": 19, "minute": 0},
    Schedule.WEEKLY_MONDAY: {"day_of_week": "mon", "hour": 9, "minute": 0},
    Schedule.WEEKLY_FRIDAY: {"day_of_week": "fri", "hour": 17, "minute": 0},
    Schedule.MONTHLY_FIRST: {"day": 1, "hour": 10, "minute": 0},
}


class AgentScheduler:
    """Manages scheduled agent runs via APScheduler."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler(timezone=_TIMEZONE)
        self._jobs: dict[str, object] = {}

    def register(
        self,
        job_id: str,
        func: Callable,
        schedule: Schedule,
        *,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> str:
        """Register a callable to run on a pre-defined schedule.

        Args:
            job_id: Unique identifier for this job.
            func: The callable to invoke (e.g. ``agent.run``).
            schedule: One of the pre-defined Schedule values.
            args: Positional arguments forwarded to *func*.
            kwargs: Keyword arguments forwarded to *func*.

        Returns:
            The *job_id* for later reference.
        """
        cron_params = _SCHEDULE_CRONS[schedule]
        trigger = CronTrigger(timezone=_TIMEZONE, **cron_params)

        job = self._scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            args=args,
            kwargs=kwargs or {},
            replace_existing=True,
        )
        self._jobs[job_id] = job
        logger.info("Registered job %s on schedule %s", job_id, schedule.value)
        return job_id

    def unregister(self, job_id: str) -> None:
        """Remove a scheduled job."""
        if job_id in self._jobs:
            self._scheduler.remove_job(job_id)
            del self._jobs[job_id]
            logger.info("Unregistered job %s", job_id)

    def start(self) -> None:
        """Start the background scheduler."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started with %d jobs", len(self._jobs))

    def stop(self) -> None:
        """Shut down the scheduler, waiting for running jobs to finish."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")

    def list_jobs(self) -> list[dict[str, str | None]]:
        """Return a summary of all registered jobs."""
        return [
            {
                "job_id": job_id,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            }
            for job_id, job in self._jobs.items()
        ]
