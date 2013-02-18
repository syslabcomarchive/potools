# -*- coding: UTF-8 -*-
from mr.developer.common import which
from optparse import OptionParser
import logging
import os
import polib
import re
import subprocess
import tempfile
import urllib
from potools import utils

LOGLEVEL = logging.INFO

logging.basicConfig(
            level=LOGLEVEL,
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def parse_options(script):
    global LOGLEVEL
    usage = "usage: %prog [options] FILE(S)"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="Verbose mode")
    parser.add_option("--vcs", nargs=2, dest="vcs",
                        help=u"Compare the file to one in a version "
                            u"control repository. Specify the version "
                            u"control type and its URL (e.g --vcs git "
                            u"git@github.com:syslabcom/potools.git).")

    (options, args) = parser.parse_args()
    if not options.vcs and len(args) != 2:
        parser.error(u"If you aren't using the --vcs option, then you'll \
                        need to specify exactly two files.")
    LOGLEVEL = options.verbose and logging.DEBUG or logging.INFO
    return (options, args)


def _vcsdiff(pofiles, vcstype, vcsurl):
    """ Internal helper function. 
    
        Diffs a file with it's counterpart in a VCS repository, of 
        type $vcstype at $vcsurl.
    """
    dir = '/'.join(pofiles[0].split('/')[:-1])
    os.chdir(dir)
    basepath = utils.get_package_root(os.getcwd())

    for pofile in pofiles:
        proto, string = urllib.splittype(vcsurl)
        host, path = urllib.splithost(string)
        relpath = os.path.relpath(pofile, basepath)
        pofileurl = os.path.join(vcsurl, relpath)
        tmp, tmppath = tempfile.mkstemp(text=True)
        if vcstype == 'svn':
            urllib.urlretrieve(pofileurl, tmppath)
        elif vcstype == 'git':
            cmd = which('git')
            branchmatch = re.search('branch=(\S*)', vcsurl)
            if branchmatch:
                branch = branchmatch.group(1)
            else:
                branch = 'master'
            cmdline = '%s show %s:%s' % (cmd, branch, relpath)
            err, errtmppath = tempfile.mkstemp(text=True)
            out = subprocess.Popen(cmdline.split(' '), 
                    stdout=subprocess.PIPE,
                    stderr=err,
                    cwd=basepath).stdout.read()
            err = open(errtmppath).read()
            if err:
                log.critical(err)
                return
            outfile = open(tmppath, 'w')
            outfile.write(out)
            outfile.close()
        else:
            log.critical('Sorry, %s is not supported yet.')
            return
        log.debug("Comparing %s and %s:%s" % (pofile, branch, relpath))
        _diff(pofile, tmppath)
        os.remove(tmppath)


def _diff(filepath1, filepath2):
    """ Internal helper function

        Diffs two po files. Only cares about msgid and msgstr, not about 
        position in the file, comments etc.
    """
    file1 = polib.pofile(filepath1)
    file2 = polib.pofile(filepath2)
    diff = []
    for entry_file2 in file2:
        entry_file1 = file1.find(
                            entry_file2.msgid,
                            include_obsolete_entries=True)
        if not entry_file1:
            diff += [u'-msgid "%s"' % entry_file2.msgid]
            diff += [u'-msgstr "%s"\n' % entry_file2.msgstr]
        elif not entry_file2.msgstr == entry_file1.msgstr:
            diff += [u' msgid "%s"' % entry_file2.msgid]
            diff += [u'-msgstr "%s"' % entry_file2.msgstr]
            diff += [u'+msgstr "%s"\n' % entry_file1.msgstr]

    for entry_file1 in filter(
                        lambda e: not file2.find(
                                        e.msgid, 
                                        include_obsolete_entries=True), 
                        file1):
        diff += [u'+msgid "%s"' % entry_file1.msgid]
        diff += [u'+msgstr "%s"\n' % entry_file1.msgstr]

    if diff:
        out = [u'']
        po_path = u'Index: %s' % filepath1 
        out += [po_path]
        out += ['='*len(po_path)]
        out += [u'--- repository']
        out += [u'+++ working copy']
        out += diff
        out += ['']
        print("\n".join([o.encode('utf-8') for o in out]))

    
def podiff():
    """ Shows the difference between two po files. Only cares about msgid and
        msgstr, not about position in the file, comments etc.
    """
    (options, args) = parse_options(__name__)
    pofiles = []
    def visit(pofiles, dirname, names):
        pofiles.extend(
            map(lambda n: os.path.join(dirname, n),
                filter(
                    lambda n: n.endswith('.po') or n.endswith('.pot'), names)))

    if not options.vcs:
        _diff(args[0], args[1])
    else:
        _vcsdiff(args, options.vcs[0], options.vcs[1])
