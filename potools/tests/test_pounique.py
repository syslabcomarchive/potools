from potools import pounique
import os
import polib
import tempfile
import unittest
import shutil
import optparse

class TestPoUniqueFiles(unittest.TestCase):
    """ """

    def _get_optargs(self, **kw):
        args = [os.getcwd()+'/../../potools/tests/locales/test.po',
                os.getcwd()+'/../../potools/tests/locales2/test.po']
        opts = {'best': False, 'sort': False, 'output': None}
        opts.update(kw)
        return pounique.parse_options(args, optparse.Values(opts))

    def test_unique_last(self):
        options, args = self._get_optargs()
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        mapping = {}
        for entry in entries:
            mapping[entry.msgid] = entry.msgstr
            
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'', 
                           u'label_foo': u'Foobar', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo'})

    def test_unique_best(self):
        options, args = self._get_optargs(best=True)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        mapping = {}
        for entry in entries:
            mapping[entry.msgid] = entry.msgstr
            
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo'})

    def test_unique_sorted(self):
        options, args = self._get_optargs(sort=True)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        self.assertEquals(
            [x.msgid for x in entries], 
            [u'Baz', u'bazoo', u'Hello World', u'label_bar', u'label_foo'])

class TestPoUniqueFolders(unittest.TestCase):
    """ """

    def _get_optargs(self, **kw):
        args = [os.getcwd()+'/../../potools/tests/locales/',
                os.getcwd()+'/../../potools/tests/locales2/']
        
        opts = {'best': False, 'sort': False, 'output': None}
        opts.update(kw)
        return pounique.parse_options(args, optparse.Values(opts))

    def test_dir(self):
        try:
            outdir = tempfile.mkdtemp()
            opts, args = self._get_optargs(output=outdir)
        finally:
            shutil.rmtree(outdir)