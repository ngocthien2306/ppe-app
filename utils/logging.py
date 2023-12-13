import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from utils.project_config import project_config as cf
import os

class CustomLoggerConfig:

    @staticmethod
    def configure_logger(log_level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        log_directory = os.path.join(cf.LOG_PATH, 'text_info')
        if not os.path.exists(log_directory):
            os.makedirs(log_directoryl
                        )
        # Create a rotating file handler that rotates logs daily
        log_file_path = f'{log_directory}/log_{datetime.now().strftime("%Y-%m-%d")}.log'
        file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=5)

        file_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(log_level)

        logger.addHandler(file_handler)

        return logger
    


