#!/usr/bin/env python3
"""
LifeLedger CLI Executable Wrapper.
Allows running the LifeLedger CLI directly from the root workspace directory.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-cli" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-sdk-py" / "src"))

from lifeledger_cli.main import cli

if __name__ == "__main__":
    cli(obj={})
