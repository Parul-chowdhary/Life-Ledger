"""
LifeLedger Command-Line Interface (CLI).
Provides terminal commands to inspect vault documents, track upcoming deadlines,
evaluate warranties, and trigger backups.
"""
import sys
from pathlib import Path
import click
import requests

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


@click.group()
@click.option("--url", default="http://127.0.0.1:5000", help="Base URL of LifeLedger server")
@click.pass_context
def cli(ctx, url):
    """LifeLedger — Personal Document, Warranty and Deadline Intelligence CLI."""
    ctx.ensure_object(dict)
    ctx.obj["BASE_URL"] = url.rstrip("/")


@cli.command()
@click.pass_context
def status(ctx):
    """Checks connection health to the LifeLedger platform."""
    url = f"{ctx.obj['BASE_URL']}/api/v1/ping"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            click.echo(f"[*] LifeLedger Server is ONLINE at {ctx.obj['BASE_URL']}")
            click.echo(f"    Payload: {resp.json()}")
        else:
            click.echo(f"[!] Server returned HTTP {resp.status_code}")
    except requests.RequestException as e:
        click.echo(f"[!] Failed to connect to {ctx.obj['BASE_URL']}: {str(e)}")


@cli.group()
def deadlines():
    """Manage deadlines and renewal obligations."""
    pass


@deadlines.command("complete")
@click.argument("deadline_id")
@click.pass_context
def complete_deadline(ctx, deadline_id):
    """Marks a deadline as completed and triggers recurrence rollover."""
    url = f"{ctx.obj['BASE_URL']}/api/v1/deadlines/{deadline_id}/complete"
    try:
        resp = requests.patch(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            click.echo(f"[+] Successfully marked deadline {deadline_id} as completed!")
            if data.get("next_occurrence"):
                click.echo(f"    Rolled over to next occurrence: {data['next_occurrence']}")
        else:
            click.echo(f"[!] Failed to complete deadline: {resp.text}")
    except requests.RequestException as e:
        click.echo(f"[!] Connection error: {str(e)}")


@cli.group()
def export():
    """Export platform data and calendar feeds."""
    pass


@export.command("ical")
@click.option("--output", "-o", default="lifeledger.ics", help="Output .ics filename")
@click.pass_context
def export_ical(ctx, output):
    """Exports RFC 5545 iCalendar feed to a file."""
    url = f"{ctx.obj['BASE_URL']}/api/v1/deadlines/ical"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(output, "w", encoding="utf-8") as f:
                f.write(resp.text)
            click.echo(f"[+] Exported iCalendar feed to: {output}")
        else:
            click.echo(f"[!] Export failed: HTTP {resp.status_code}")
    except Exception as e:
        click.echo(f"[!] Error: {str(e)}")


@export.command("csv")
@click.option("--output", "-o", default="lifeledger_vault.csv", help="Output .csv filename")
@click.pass_context
def export_csv(ctx, output):
    """Exports vault metadata to a CSV file."""
    url = f"{ctx.obj['BASE_URL']}/analytics/export-csv"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(output, "w", encoding="utf-8") as f:
                f.write(resp.text)
            click.echo(f"[+] Exported Vault CSV data to: {output}")
        else:
            click.echo(f"[!] Export failed: HTTP {resp.status_code}")
    except Exception as e:
        click.echo(f"[!] Error: {str(e)}")


if __name__ == "__main__":
    cli(obj={})
