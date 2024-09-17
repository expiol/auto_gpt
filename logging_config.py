import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Check and create logs directory
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        print(f"Created log directory at {os.path.abspath(log_directory)}")

    # Create log handler
    log_file = os.path.join(log_directory, 'app.log')
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    handler.setLevel(logging.DEBUG)

    # Create log formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Console log output
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

