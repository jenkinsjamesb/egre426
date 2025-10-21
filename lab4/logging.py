'''
logging.py

BRISC logging function file

James Jenkins 2025
'''

import datetime
import inspect
import os

def init_log(logfile="run.log", quiet=True, default_level="INFO"):
        global LOGFILE
        global ENABLE_QUIET_LOGGING
        global DEFAULT_LOG_LEVEL

        LOGFILE = logfile
        ENABLE_QUIET_LOGGING = quiet
        DEFAULT_LOG_LEVEL = default_level

def log(text, level=None):
        with open (LOGFILE, "a") as logfile:
                timestamp = datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
                filename = os.path.basename(inspect.stack()[1].filename)

                if level == None:
                        level = DEFAULT_LOG_LEVEL
                else:
                        level = level.upper()

                logstring = f"[{timestamp}] [{level}] [{filename}] {text}"

                logstring = logstring.replace("\n", "\n|\t") + "\n"

                logfile.write(logstring)

                if not ENABLE_QUIET_LOGGING:
                        print(logstring[:-1])

