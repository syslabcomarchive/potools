# -*- coding: UTF-8 -*-
import logging
import os
import polib
import re
import subprocess
import tempfile
import urllib
from mr.developer.common import which
from potools import utils

logging.basicConfig(
            level=utils.loglevel(),
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def podiff():
    """ %(program)s: shows differences between the po files in the current 
        subdirectory tree  and their counterparts in a repository. 
        Only cares about msgid and msgstr, not about position in the file, 
        comments, etc.

        Usage:  %(program)s [--help|-h] [-v] ${VCS type} ${VCS URL}
    """
    options = utils.parse_options(__name__)
    if options.vcs:
        vcstype = options.vcs[0]
        vcsurl = options.vcs[1]

    pofiles = []
    def visit(pofiles, dirname, names):
        pofiles.extend(
            map(lambda n: os.path.join(dirname, n),
                filter(
                    lambda n: n.endswith('.po') or n.endswith('.pot'), names)))

    if options.file:
        file = options.file
        pofiles = [file]
        dir = '/'.join(options.file.split('/')[:-1])
        os.chdir(dir)
        basepath = utils.get_package_root(os.getcwd())
    else:
        if options.dir:
            os.chdir(options.dir)
        cwd = os.getcwd()
        os.path.walk(cwd, visit, pofiles)
        basepath = utils.get_package_root(cwd)

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
        polocal = polib.pofile(pofile)
        povcs = polib.pofile(tmppath)

        diff = []
        for entryvcs in povcs:
            entrylocal = polocal.find(
                                entryvcs.msgid,
                                include_obsolete_entries=True)
            if not entrylocal:
                diff += [u'-msgid "%s"' % entryvcs.msgid]
                diff += [u'-msgstr "%s"\n' % entryvcs.msgstr]
            elif not entryvcs.msgstr == entrylocal.msgstr:
                diff += [u' msgid "%s"' % entryvcs.msgid]
                diff += [u'-msgstr "%s"' % entryvcs.msgstr]
                diff += [u'+msgstr "%s"\n' % entrylocal.msgstr]

        for entrylocal in filter(
                            lambda e: not povcs.find(
                                            e.msgid, 
                                            include_obsolete_entries=True), 
                            polocal):
            diff += [u'+msgid "%s"' % entrylocal.msgid]
            diff += [u'+msgstr "%s"\n' % entrylocal.msgstr]

        if diff:
            out = [u'']
            po_path = u'Index: %s' % pofile
            out += [po_path]
            out += ['='*len(po_path)]
            out += [u'--- repository']
            out += [u'+++ working copy']
            out += diff
            out += ['']
            print("\n".join([o.encode('utf-8') for o in out]))

        os.remove(tmppath)
