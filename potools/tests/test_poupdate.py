from potools import poupdate
import os
import polib
import tempfile
import unittest
import shutil
import optparse

class TestPoUpdateFiles(unittest.TestCase):
    """ """

    def setUp(self):
        self.target = tempfile.mkstemp()[1]
        shutil.copy(os.getcwd()+'/../../potools/tests/locales/test.po',
                    self.target)
        self.source = os.getcwd()+'/../../potools/tests/locales2/test.po'
        
    def tearDown(self):
        os.unlink(self.target)
        
    def _get_optargs(self, **kw):        
        opts = {'insert_new': False, 'force': False}
        opts.update(kw)
        return poupdate.parse_options([self.target, self.source], optparse.Values(opts))

    def test_update(self):
        options, args = self._get_optargs()
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World'})
        
    def test_update_insert(self):
        options, args = self._get_optargs(insert_new=True)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo'})
        
    def test_update_force(self):
        options, args = self._get_optargs(force=True)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'', 
                           u'label_foo': u'Foobar', 
                           u'Hello World': u'Hello World'})
        
