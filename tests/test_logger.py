import pytest
from pathlib import Path
from src.core.logger import AppLogger


class TestAppLogger:
    """Test logging functionality with file and callback support."""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create logger with temp log file."""
        log_file = tmp_path / "test.log"
        return AppLogger(log_file)

    @pytest.fixture
    def logger_no_file(self):
        """Create logger without file output."""
        return AppLogger(None)

    # Basic Logging Tests
    def test_logger_creates_log_file(self, tmp_path):
        """Logger should create log file on first write."""
        log_file = tmp_path / "test.log"
        logger = AppLogger(log_file)

        logger.info("Test message")

        assert log_file.exists()

    def test_logger_without_file_doesnt_crash(self, logger_no_file):
        """Logger should work without a log file."""
        # Should not raise exception
        logger_no_file.info("Test message")
        logger_no_file.error("Error message")

    def test_debug_logging(self, logger):
        """Should log debug messages."""
        logger.debug("Debug message")

        contents = logger.get_log_contents()
        assert "Debug message" in contents
        assert "DEBUG" in contents

    def test_info_logging(self, logger):
        """Should log info messages."""
        logger.info("Info message")

        contents = logger.get_log_contents()
        assert "Info message" in contents
        assert "INFO" in contents

    def test_warning_logging(self, logger):
        """Should log warning messages."""
        logger.warning("Warning message")

        contents = logger.get_log_contents()
        assert "Warning message" in contents
        assert "WARNING" in contents

    def test_error_logging(self, logger):
        """Should log error messages."""
        logger.error("Error message")

        contents = logger.get_log_contents()
        assert "Error message" in contents
        assert "ERROR" in contents

    def test_success_logging(self, logger):
        """Success messages should be logged as info with checkmark."""
        logger.success("Operation succeeded")

        contents = logger.get_log_contents()
        assert "Operation succeeded" in contents
        assert "✓" in contents

    # Callback Tests
    def test_ui_callback_called(self, logger_no_file):
        """UI callback should be called for each log."""
        messages = []

        def callback(message, level):
            messages.append((message, level))

        logger_no_file.set_ui_callback(callback)
        logger_no_file.info("Test message")

        assert len(messages) == 1
        assert messages[0][0] == "Test message"
        assert messages[0][1] == "info"

    def test_status_callback_called(self, logger_no_file):
        """Status callback should be called for non-debug logs."""
        messages = []

        def callback(message, level):
            messages.append((message, level))

        logger_no_file.set_status_callback(callback)
        logger_no_file.info("Info message")
        logger_no_file.warning("Warning message")

        assert len(messages) == 2
        assert messages[0][0] == "Info message"
        assert messages[1][0] == "Warning message"

    def test_status_callback_not_called_for_debug(self, logger_no_file):
        """Status callback should NOT be called for debug messages."""
        messages = []

        def callback(message, level):
            messages.append((message, level))

        logger_no_file.set_status_callback(callback)
        logger_no_file.debug("Debug message")

        assert len(messages) == 0

    def test_both_callbacks_called(self, logger_no_file):
        """Both UI and status callbacks should be called."""
        ui_messages = []
        status_messages = []

        def ui_callback(message, level):
            ui_messages.append(message)

        def status_callback(message, level):
            status_messages.append(message)

        logger_no_file.set_ui_callback(ui_callback)
        logger_no_file.set_status_callback(status_callback)
        logger_no_file.info("Test message")

        assert len(ui_messages) == 1
        assert len(status_messages) == 1

    def test_callback_exception_doesnt_crash(self, logger_no_file):
        """Logger should not crash if callback raises exception."""
        def bad_callback(message, level):
            raise ValueError("Callback error")

        logger_no_file.set_ui_callback(bad_callback)

        # Should not raise exception
        logger_no_file.info("Test message")

    # Log File Operations
    def test_get_log_contents_empty(self, tmp_path):
        """Should return empty string for non-existent log."""
        log_file = tmp_path / "nonexistent.log"
        logger = AppLogger(log_file)

        contents = logger.get_log_contents()

        assert contents == ""

    def test_get_log_contents_with_data(self, logger):
        """Should return log file contents."""
        logger.info("Message 1")
        logger.error("Message 2")

        contents = logger.get_log_contents()

        assert "Message 1" in contents
        assert "Message 2" in contents

    def test_clear_logs(self, logger):
        """Should clear log file contents."""
        logger.info("Message before clear")
        logger.clear_logs()

        contents = logger.get_log_contents()

        assert "Message before clear" not in contents
        assert "Logs cleared" in contents

    def test_clear_logs_without_file(self, logger_no_file):
        """Clearing logs without file should not crash."""
        # Should not raise exception
        logger_no_file.clear_logs()

    # Multiple Messages
    def test_multiple_log_levels(self, logger):
        """Should log multiple different levels correctly."""
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        logger.success("Success")

        contents = logger.get_log_contents()

        assert "Debug" in contents
        assert "Info" in contents
        assert "Warning" in contents
        assert "Error" in contents
        assert "Success" in contents

    def test_log_order_preserved(self, logger):
        """Logs should appear in order they were written."""
        logger.info("First")
        logger.info("Second")
        logger.info("Third")

        contents = logger.get_log_contents()

        first_pos = contents.find("First")
        second_pos = contents.find("Second")
        third_pos = contents.find("Third")

        assert first_pos < second_pos < third_pos

    @pytest.mark.parametrize("message", [
        "Simple message",
        "Message with 'quotes'",
        "Message with \"double quotes\"",
        "Multi\nline\nmessage",
        "Unicode: 测试消息",
        "Special chars: !@#$%^&*()",
        "",  # Empty message
    ])
    def test_various_message_formats(self, logger, message):
        """Should handle various message formats."""
        logger.info(message)

        contents = logger.get_log_contents()
        # For empty messages, just check it doesn't crash
        if message:
            assert message in contents

    def test_high_volume_logging(self, logger):
        """Should handle many log messages."""
        for i in range(100):
            logger.info(f"Message {i}")

        contents = logger.get_log_contents()

        assert "Message 0" in contents
        assert "Message 50" in contents
        assert "Message 99" in contents

    # Callback Isolation
    def test_ui_callback_independent_of_status(self, logger_no_file):
        """UI callback should work independently of status callback."""
        ui_messages = []

        def ui_callback(message, level):
            ui_messages.append(message)

        logger_no_file.set_ui_callback(ui_callback)
        logger_no_file.debug("Debug message")

        # UI should get debug, status should not
        assert len(ui_messages) == 1

    # Log File Path Tests
    def test_log_file_in_nested_directory(self, tmp_path):
        """Should create nested directories for log file."""
        log_file = tmp_path / "nested" / "dir" / "test.log"
        logger = AppLogger(log_file)

        logger.info("Test")

        assert log_file.exists()
        assert log_file.parent.exists()
