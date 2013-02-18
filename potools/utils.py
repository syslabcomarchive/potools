from optparse import OptionParser
import logging
import os
import polib
import re
import sys

VERBOSE = False
HELP = False

def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if VERBOSE:
        return logging.DEBUG
    return logging.INFO

logging.basicConfig(
            level=loglevel(),
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def get_package_root(dir=None):
    if dir is None:
        dir = os.getcwd()
    while 'setup.py' not in os.listdir(dir):
        newdir = os.path.dirname(dir)
        if newdir == dir:
            log.critical("Couldn't find python package root.")
            return 
        dir = newdir
    return dir
        

def usage(stream, func, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, func.__doc__ % {"program": program}
    sys.exit(0)


def get_default(entry):
    """ Extract the default translation from the entry (without "Default:")
    """
    patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)
    match = patt.match(entry.comment)
    # Write the "Default: " text into the msgstr. Reason: Many translators will
    # not see comments in their translation program.
    default = entry.msgid
    if match:
        default = match.group(1).replace('\n', ' ')
        if "Default:" in default:
            print "ERROR! There seems to be a duplicate Default entry for " \
                "msgid '%s'" % entry.msgid
    else:
        print "WARNING! msgid '%s' in 'new' file does not have a default " \
            "translation." % entry.msgid
        default = entry.msgid
    return default

def append_entry(pofile, entry, default):
    """ """
    pofile.append(
        polib.POEntry(
                    msgid=entry.msgid,
                    msgstr=default.strip(),
                    occurrences=entry.occurrences,
                    comment=entry.comment)
                )
    return pofile

def parse_options(script):
    global VERBOSE
    parser = OptionParser()
    parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="Verbose mode")

    if script == 'potools.podiff':
        parser.add_option("--vcs", nargs=2, dest="vcs",
                            help=u"Compare the file to one in a version "
                                u"control repository. Specify the version "
                                u"control type and its URL (e.g --vcs git "
                                u"git@github.com:syslabcom/potools.git).")
        parser.add_option("-d", "--dir", dest="dir",
                            help=u"Look for po files to be diffed in the "
                                u"subtree directory branching out from $dir. "
                                u"Cannot be used together with '-f' or '--file'")
        parser.add_option("-f", "--file", dest="file",
                            help=u"Specify the file that needs to be diffed. "
                                u"Cannot be used in together with '-d' or "
                                u"'--dir'.")

    (options, args) = parser.parse_args()

    if script == 'potools.podiff':
        if options.dir and options.file:
            parser.error("Options -f and -d are mutually exclusive")
        if not options.vcs:
            parser.error("Sorry, non-VCS diffing not yet implemented.")
            
    VERBOSE = options.verbose
    return options
    
