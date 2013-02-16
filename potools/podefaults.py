import sys
import os
import re
import polib
import logging
from potools import utils

logging.basicConfig(
            level=utils.loglevel(),
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

def usage(stream, func, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, func.__doc__ % {"program": program}
    sys.exit(0)

def podefaults():
    """%(program)s: Parses a given .po file and shouts a warning for every 
        entry that has more than one Default entry.

        usage:    %(program)s file.po
        file.po   A po to check
        --debug   Print debug statistics.
    """
    patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)

    if len(sys.argv) < 2:
        usage(sys.stderr, u"\nERROR: Not enough arguments")
    filename = sys.argv[1]

    debug = False
    for i in range(1, len(sys.argv)):
        arg = sys.argv.pop()
        if arg == "--debug":
            debug = True

    po = polib.pofile(filename)
    counter = 0

    for entry in po:
        counter += 1
        match = patt.match(entry.comment)
        if match:
            default = match.group(1).replace('\n', ' ')
            if "Default:" in default:
                log.error(u"Duplicate default for msgid '%s'" % entry.msgid)
        else:
            if debug:
                log.warn(u"No Default translation for msgid '%s'." %
                        entry.msgid)

    sys.exit('Finished, checked all %d entries.' % counter)
