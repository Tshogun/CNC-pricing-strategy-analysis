import logging
import os

def setup_logger():
    """
    Set up the logger to log messages to both the console and different files,
    ensuring only INFO and ERROR levels are shown in the console and logs are saved in multiple files in the same folder as logger.py.
    """
    # Get the directory where the logger.py file is located
    log_dir = os.path.dirname(os.path.abspath(__file__))

    logger = logging.getLogger("CNCProductScraper")
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG (captures all log levels)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (output logs to the console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Only show INFO and ERROR on the console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handlers (output logs to different files in the same folder as logger.py)
    # File handler 1 - Stores INFO, ERROR and above logs in this file
    file_handler_1 = logging.FileHandler(os.path.join(log_dir, 'log_1.log'))
    file_handler_1.setLevel(logging.INFO)  # Store INFO, ERROR and above
    file_handler_1.setFormatter(formatter)
    logger.addHandler(file_handler_1)

    # File handler 2 - Stores INFO, ERROR and above logs in this file
    file_handler_2 = logging.FileHandler(os.path.join(log_dir, 'log_2.log'))
    file_handler_2.setLevel(logging.INFO)  # Store INFO, ERROR and above
    file_handler_2.setFormatter(formatter)
    logger.addHandler(file_handler_2)

    # File handler 3 - Stores ERROR and above logs in this file
    file_handler_3 = logging.FileHandler(os.path.join(log_dir, 'log_3.log'))
    file_handler_3.setLevel(logging.ERROR)  # Store ERROR and above
    file_handler_3.setFormatter(formatter)
    logger.addHandler(file_handler_3)

    return logger
