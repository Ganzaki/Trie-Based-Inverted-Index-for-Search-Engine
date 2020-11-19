"""
    Logs into log file
"""
from datetime import datetime
from config import LOG_FILE



def logger(msg, *args, **kwargs):
    """
        logs error into logs file
    """
    now = datetime.now()
    log = open(LOG_FILE, "a")
    log.write(str(now))
    log.write(" : ")
    log.write(str(msg))
    log.write("\n")
    for arg in args:
        log.write(str(now))
        log.write(" : ")
        log.write(str(arg))
        log.write("\n")

    for key in kwargs:
        log.write(str(now))
        log.write(" : ")
        log.write(str(key))
        log.write("-")
        log.write(str(kwargs[key]))
