import logging
import os

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger that writes logs to a file and optionally to the console.

    Parameters:
    - name (str): Logger name.
    - log_file (str): File path to save the logs.
    - level (int): Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
    - logging.Logger: Configured logger instance.
    """
    # Create logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate log handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Optional: Console handler (if you want to log to the console as well)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
