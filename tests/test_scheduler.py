"""
Tests for integrations.scheduler — AgentScheduler and Schedule enum.
"""
from unittest.mock import MagicMock, patch

import pytest

from integrations.scheduler import Schedule, _SCHEDULE_CRONS


# ── Schedule enum ────────────────────────────────────────────────────────


def test_all_schedules_have_cron_config():
    for schedule in Schedule:
        assert schedule in _SCHEDULE_CRONS


def test_daily_evening_is_7pm():
    cron = _SCHEDULE_CRONS[Schedule.DAILY_EVENING]
    assert cron["hour"] == 19
    assert cron["minute"] == 0


def test_weekly_monday_is_9am():
    cron = _SCHEDULE_CRONS[Schedule.WEEKLY_MONDAY]
    assert cron["day_of_week"] == "mon"
    assert cron["hour"] == 9


def test_monthly_first_is_10am():
    cron = _SCHEDULE_CRONS[Schedule.MONTHLY_FIRST]
    assert cron["day"] == 1
    assert cron["hour"] == 10


# ── AgentScheduler ───────────────────────────────────────────────────────


@patch("integrations.scheduler.BackgroundScheduler", autospec=True)
def test_register_and_list_jobs(mock_scheduler_cls):
    # Avoid real import; patch at module level
    from integrations.scheduler import AgentScheduler

    mock_scheduler = MagicMock()
    mock_scheduler_cls.return_value = mock_scheduler

    mock_job = MagicMock()
    mock_job.next_run_time = "2026-04-23 19:00:00+05:30"
    mock_scheduler.add_job.return_value = mock_job

    sched = AgentScheduler()
    job_id = sched.register("daily_brief", lambda: None, Schedule.DAILY_EVENING)

    assert job_id == "daily_brief"
    jobs = sched.list_jobs()
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "daily_brief"


@patch("integrations.scheduler.BackgroundScheduler", autospec=True)
def test_unregister_removes_job(mock_scheduler_cls):
    from integrations.scheduler import AgentScheduler

    mock_scheduler = MagicMock()
    mock_scheduler_cls.return_value = mock_scheduler
    mock_scheduler.add_job.return_value = MagicMock(next_run_time=None)

    sched = AgentScheduler()
    sched.register("job1", lambda: None, Schedule.WEEKLY_MONDAY)
    sched.unregister("job1")

    mock_scheduler.remove_job.assert_called_once_with("job1")
    assert sched.list_jobs() == []


@patch("integrations.scheduler.BackgroundScheduler", autospec=True)
def test_unregister_noop_for_unknown_job(mock_scheduler_cls):
    from integrations.scheduler import AgentScheduler

    mock_scheduler_cls.return_value = MagicMock()
    sched = AgentScheduler()
    sched.unregister("nonexistent")  # should not raise


@patch("integrations.scheduler.BackgroundScheduler", autospec=True)
def test_start_and_stop(mock_scheduler_cls):
    from integrations.scheduler import AgentScheduler

    mock_scheduler = MagicMock()
    mock_scheduler.running = False
    mock_scheduler_cls.return_value = mock_scheduler

    sched = AgentScheduler()
    sched.start()
    mock_scheduler.start.assert_called_once()

    mock_scheduler.running = True
    sched.stop()
    mock_scheduler.shutdown.assert_called_once_with(wait=True)
