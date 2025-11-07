"""
Reset the local database, ingest/process data, and start the Streamlit app.

This mirrors the Makefile target `reset-and-up` by executing:
  1) data/clear_db.py
  2) models/__init__.py (creates tables)
  3) data/db_seeds.py
  4) src/ingest/roster.py
  5) src/ingest/player.py
  6) src/ingest/schedule.py
  7) src/process/player_schedule_points.py
  8) streamlit run main.py

Usage:
  poetry run python reset_and_up.py

Flags:
  --skip-streamlit      Skip launching Streamlit after data setup
  --only-streamlit      Only launch Streamlit (skip all data steps)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
import logging
import logging.config
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parent


def setup_logging() -> None:
    config_path = PROJECT_ROOT / "logging.ini"
    if config_path.exists():
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def run_command(command: List[str]) -> None:
    """Run a command, streaming output; raise on nonzero exit."""
    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
    ret = process.wait()
    if ret != 0:
        raise RuntimeError(f"Command failed with exit code {ret}: {' '.join(command)}")


def python_exec() -> str:
    """Return the current Python executable path."""
    return sys.executable


def step_clear_db() -> None:
    logger.info("[1/7] Clearing database...")
    from data.clear_db import clear_db

    clear_db()
    logger.info("[1/7] Done clearing database")


def step_create_tables() -> None:
    logger.info("[2/7] Creating database tables...")
    from models import create_tables

    create_tables()
    logger.info("[2/7] Done creating database tables")


def step_seed_db() -> None:
    logger.info("[3/7] Seeding database tables...")
    from data.db_seeds import seed_db

    seed_db()
    logger.info("[3/7] Done seeding database tables")


def step_ingest() -> None:
    logger.info("[4/7] Ingesting roster data...")
    from src.ingest.roster import ingest_rosters

    ingest_rosters()
    logger.info("[5/7] Ingesting player data...")
    from src.ingest.player import ingest_players

    ingest_players()
    logger.info("[6/7] Ingesting schedule data...")
    from src.ingest.schedule import ingest_schedule

    ingest_schedule()
    logger.info("[4-6/7] Done ingesting data")


def step_process() -> None:
    logger.info("[7/7] Processing player schedule points...")
    from src.process.player_schedule_points import process_player_schedule_points

    process_player_schedule_points()
    logger.info("[7/7] Done processing player schedule points")


def launch_streamlit() -> None:
    logger.info("[APP] Launching Streamlit app at main.py ... Press Ctrl+C to stop.")
    # Use `python -m streamlit` to ensure we use the same interpreter/environment
    run_command([python_exec(), "-m", "streamlit", "run", "main.py"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset DB, ingest/process, and run Streamlit."
    )
    parser.add_argument(
        "--skip-streamlit",
        action="store_true",
        help="Skip launching Streamlit after data setup",
    )
    parser.add_argument(
        "--only-streamlit",
        action="store_true",
        help="Only launch Streamlit (skip all data steps)",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    logger.info("Starting reset and up sequence")
    args = parse_args()

    if args.only_streamlit:
        launch_streamlit()
        return

    # Full reset-and-up sequence
    try:
        step_clear_db()
        step_create_tables()
        step_seed_db()
        step_ingest()
        step_process()
    except Exception:
        logger.exception("Error during reset-and-up sequence")
        raise

    if not args.skip_streamlit:
        launch_streamlit()
    else:
        logger.info(
            "[DONE] Data reset and processing completed. Streamlit launch skipped."
        )


if __name__ == "__main__":
    # Ensure we run from project root for relative paths
    os.chdir(PROJECT_ROOT)
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     logger.warning("Interrupted by user.")
    # except Exception as exc:
    #     logger.error("Fatal error: %s", exc)
    # sys.exit(1)
