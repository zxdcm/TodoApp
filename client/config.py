import os


APP_DATA_DIRECTORY = os.path.join(os.environ['HOME'], 'todoapp')
DATABASE_PATH = APP_DATA_DIRECTORY
CONNECTION_STRING = os.path.join(DATABASE_PATH, 'todoapp.db')
CONFIG_FILE = os.path.join(APP_DATA_DIRECTORY, 'config.ini')
LOG_ENABLED = True
LOGS_DIRECTORY = APP_DATA_DIRECTORY
LOG_FILE = 'todoapp.log'
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
