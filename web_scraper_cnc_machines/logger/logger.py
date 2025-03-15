import logging

def setup_logger(log_file="app.log"):
    """
    Set up the logger to log messages to both the console and a file.
    
    Args:
        log_file (str): The name of the log file to which logs will be saved.
    """
    logger = logging.getLogger("CNCProductScraper")
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG (captures all log levels)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (output logs to the console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (output logs to a file)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
