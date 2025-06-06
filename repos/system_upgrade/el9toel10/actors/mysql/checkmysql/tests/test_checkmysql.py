import pytest

from leapp import reporting
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.actor import checkmysql
from leapp.libraries.common.testutils import create_report_mocked, logger_mocked
from leapp.libraries.stdlib import api
from leapp.models import MySQLConfiguration


def test_process_no_msg(monkeypatch):
    def consume_mocked(*args, **kwargs):
        yield None

    monkeypatch.setattr(api, 'consume', consume_mocked)

    with pytest.raises(StopActorExecutionError):
        checkmysql.process()


def test_process_no_mysql(monkeypatch):
    def consume_mocked(*args, **kwargs):
        yield MySQLConfiguration(mysql_present=False,
                                 removed_options=[],
                                 removed_arguments=[])

    monkeypatch.setattr(api, 'current_logger', logger_mocked())
    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'consume', consume_mocked)

    checkmysql.process()
    assert (
        'mysql-server package not found, no report generated'
        in api.current_logger.dbgmsg
    )
    assert len(reporting.create_report.reports) == 0


def test_process_no_deprecated(monkeypatch):
    def consume_mocked(*args, **kwargs):
        yield MySQLConfiguration(mysql_present=True,
                                 removed_options=[],
                                 removed_arguments=[])

    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'consume', consume_mocked)

    checkmysql.process()

    # Check that we have made a report
    assert len(reporting.create_report.reports) == 1


def test_process_deprecated(monkeypatch):
    def consume_mocked(*args, **kwargs):
        yield MySQLConfiguration(mysql_present=True,
                                 removed_options=['avoid_temporal_upgrade', '--old'],
                                 removed_arguments=['--language'])

    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'consume', consume_mocked)

    checkmysql.process()

    # Check that we have made a report
    assert len(reporting.create_report.reports) == 2

    # Find deprecation report
    found = None
    for rep in reporting.create_report.reports:
        if rep['title'] == 'Detected incompatible MySQL configuration':
            found = rep
            break

    assert found is not None

    r = found['summary']

    # Check that Hint was in the report
    assert r is not None

    # Check that we informed user about all the deprecated options
    assert 'avoid_temporal_upgrade' in r
    assert '--old' in r
    assert '--language' in r
