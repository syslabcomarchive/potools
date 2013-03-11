from optparse import OptionParser
import logging
import polib
import re
import sys

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")
    parser.add_option("--defaults", action="store_true",
                      dest="defaults", default=False,
                      help=u"Check for duplicate default entries.")

    (options, args) = parser.parse_args(args, values)
    if len(args) != 1:
        parser.error(u"Invalid number of arguments.")
    return (options, args)


class PoCheck(object):
    """ Check a po file for various smells.
    """

    def __init__(self, args=(), options={}):
        self.options = options
        self.args = args

    def run(self):
        """ """
        if self.options.defaults:
            out = self.check_duplicate_defaults()
            print out
            sys.exit(0)

    def check_duplicate_defaults(self):
        patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)
        po = polib.pofile(self.args[0])
        counter = 0
        out = ''
        for entry in po:
            counter += 1
            match = patt.match(entry.comment)
            if match:
                if "Default:" in match.group(1).replace('\n', ' '):
                    out += 'Duplicate for msgid "%s"\n' % entry.msgid
        return out


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=options.verbose and logging.DEBUG or logging.INFO,
        format="%(levelname)s: %(message)s")
    PoCheck(args, options).run()
