"""Centralized logging system for the application."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable


class AppLogger:
    """Application logger with file and UI output."""

    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize logger.

        Args:
            log_file: Path to log file (optional)
        """
        self.log_file = log_file
        self.ui_callback: Optional[Callable[[str, str], None]] = None
        self.status_callback: Optional[Callable[[str, str], None]] = None

        # Setup Python logging
        self.logger = logging.getLogger('FM26ModManager')
        self.logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self.logger.handlers = []

        # Console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if log file provided
        if self.log_file:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to create log file handler: {e}")

    def set_ui_callback(self, callback: Callable[[str, str], None]):
        """
        Set callback for UI log updates.

        Args:
            callback: Function that takes (message, level) and updates UI
        """
        self.ui_callback = callback

    def set_status_callback(self, callback: Callable[[str, str], None]):
        """
        Set callback for status bar updates.

        Args:
            callback: Function that takes (message, level) and updates status bar
        """
        self.status_callback = callback

    def _log(self, level: str, message: str):
        """
        Internal log method.

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
        """
        # Log to Python logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)

        # Call UI callback if set
        if self.ui_callback:
            try:
                self.ui_callback(message, level)
            except Exception:
                pass  # Don't let UI errors break logging

        # Call status callback if set (only for non-debug messages)
        if self.status_callback and level != 'debug':
            try:
                self.status_callback(message, level)
            except Exception:
                pass  # Don't let UI errors break logging

    def debug(self, message: str):
        """Log debug message."""
        self._log('debug', message)

    def info(self, message: str):
        """Log info message."""
        self._log('info', message)

    def warning(self, message: str):
        """Log warning message."""
        self._log('warning', message)

    def error(self, message: str):
        """Log error message."""
        self._log('error', message)

    def success(self, message: str):
        """Log success message (treated as info)."""
        self._log('info', f"✓ {message}")

    def get_log_contents(self) -> str:
        """
        Read and return log file contents.

        Returns:
            Log file contents as string, or empty string if no file
        """
        if not self.log_file or not self.log_file.exists():
            return ""

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def clear_logs(self):
        """Clear the log file."""
        if self.log_file and self.log_file.exists():
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"--- Logs cleared at {datetime.now().isoformat()} ---\n")
            except Exception:
                pass
