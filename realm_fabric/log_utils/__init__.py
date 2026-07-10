"""
Logging utilities.

Contains helpers for rich console output and file logging during simulation runs.
This replaces the need for stdlib 'logging' to avoid name conflicts.
"""
from __future__ import annotations

from realm_fabric.log_utils.logger import (
    close_file_logging,
    log_error,
    log_turn,
    setup_file_logging,
)