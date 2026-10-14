"""
Unit Tests for LifeLedger CLI.
Uses Click's CliRunner to test command line execution.
"""
from click.testing import CliRunner
from lifeledger_cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "LifeLedger — Personal Document, Warranty and Deadline Intelligence CLI." in result.output


def test_cli_status_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "[*] LifeLedger Server is ONLINE" in result.output


def test_cli_export_ical():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "ical", "--output", "feed.ics"])
        assert result.exit_code == 0
        assert "[+] Exported iCalendar feed" in result.output


def test_cli_export_csv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "csv", "--output", "vault.csv"])
        assert result.exit_code == 0
        assert "[+] Exported Vault CSV data" in result.output
