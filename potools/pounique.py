from optparse import OptionParser
from potools import utils
from collections import defaultdict
import logging
import polib
import sys

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE1 FILE2 ..."
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")

    (options, args) = parser.parse_args(args, values)
    if len(args) < 2:
        parser.error(u"You have to name two or more po files")
    return (options, args)

def msgstr_sortkey(msg):
    return 'fuzzy' not in msg.flags, len(msg.msgstr)

class PoUnique(object):
    """ Compare two or more po files and generate a po merged po file with no duplicate entries. 
    
        With conflicting entries non-fuzzy will take precedence over fuzzy,
        and then the longest message win.

        Output is printed to stdout, in the format as a valid po file, so that
        it can be sent to translator.
    """

    def __init__(self, args=(), options={}):
        self.options = options
        self.args = args

    def run(self):
        """ """
        unique_entries = self._get_unique()
        outpo = self._generate_pofile(unique_entries)
        print outpo
        sys.exit(0)

    def _get_unique(self):
        all_entries = defaultdict(list)
        for path in self.args:
            po = polib.pofile(path)
            for entry in po:
                all_entries[entry.msgid].append(entry)
            
        entries = {}    
        for k, v in all_entries.items():
            yield sorted(v, key=msgstr_sortkey)[-1]
            
    def _generate_pofile(self, entries):
        outpo = polib.POFile()
        firstpo = polib.pofile(self.args[0])
        # Copy header and metadata
        outpo.header = firstpo.header
        for (key, val) in firstpo.metadata.items():
            outpo.metadata.update({key: val})
        for e in entries:
            outpo = utils.append_entry(outpo, e)
        return outpo


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=options.verbose and logging.DEBUG or logging.INFO,
        format="%(levelname)s: %(message)s")
    pogetnew = PoUnique(args, options)
    pogetnew.run()
