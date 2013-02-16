import logging
import sys
import os

def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if len(sys.argv) > 1:
        if '-v' in sys.argv:
            return logging.DEBUG
    return logging.INFO

logging.basicConfig(
            level=loglevel(),
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

def get_package_root():
    curdir = os.getcwd()
    while 'setup.py' not in os.listdir(curdir):
        newdir = os.path.dirname(curdir)
        if newdir == curdir:
            log.critical("Couldn't find python package root.")
            return 
        curdir = newdir
    return curdir
        

def usage(stream, func, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, func.__doc__ % {"program": program}
    sys.exit(0)

