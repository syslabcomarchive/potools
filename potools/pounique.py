from optparse import OptionParser
from potools import utils
from collections import defaultdict
import logging
import polib
import sys
import os

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE1 FILE2 ..."
    parser = OptionParser(usage)
    parser.add_option("-s", "--sort",
                      action="store_true", dest="sort", default=False,
                      help="Sort output on msgid")
    parser.add_option("-b", "--best-match",
                      action="store_true", dest="best", default=False,
                      help='Choose the "best" msgstr instead of the last.')
    parser.add_option("-o", "--output",
                      dest="output", default=None,
                      help='Output file or directory. Defaults to standardout.')

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
        if options.output is None:
            self.isdir = False
        else:
            self.isdir = os.path.isdir(options.output)
        
        argtypes = [os.path.isdir(path) for path in args]
        if any(argtypes) and not all(argtypes):
            raise ValueError('Arguments must all be files or all be directories.')

        if any(argtypes) and not self.isdir:
            raise ValueError('When inputs are directories, the output must also be a directory.')
                    

    def run(self):
        """ """
        if not self.options.output:
            print outpo
        else:
            outpo.save(self.options.output)
                
        sys.exit(0)
        
    def _get_all_comparisons(self):
        if not self.isdir:
            return self.args
        
        for path in self._get_all_unique_paths():
            pass
        
    def _get_all_unique_paths(self):
        pass
        
    def _make_unique_po(self, filepaths):
        unique_entries = self._get_unique(filepaths)
        return self._generate_pofile(unique_entries)

    def _get_unique(self, filepaths):
        all_entries = defaultdict(list)
        for path in filepaths:
            po = polib.pofile(path)
            for entry in po:
                all_entries[entry.msgid].append(entry)
            
        entries = {}
        entry_list = all_entries.keys()
        if self.options.sort:
            entry_list = sorted(entry_list, key = lambda x: x.lower())
        for k in entry_list:
            v = all_entries[k]
            if self.options.best:
                yield sorted(v, key=msgstr_sortkey)[-1]
            else:
                yield v[-1]
            
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
        level=logging.INFO,
        format="%(levelname)s: %(message)s")
    pogetnew = PoUnique(args, options)
    pogetnew.run()
