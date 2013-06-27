from potools import pounique
import os
import polib
import tempfile
import unittest
import shutil
import optparse

class TestPoUnique(unittest.TestCase):
    """ """

    def setUp(self):
        self.pf1 = os.getcwd()+'/../../potools/tests/locales/test.po'
        self.pf2 = os.getcwd()+'/../../potools/tests/locales/test2.po'

    def test_unique(self):
        unique = pounique.PoUnique(args=(self.pf1, self.pf2))
        entries = list(unique._get_unique())
        self.assertEquals(len(entries), 4)
        
        mapping = {}
        for entry in entries:
            mapping[entry.msgid] = entry.msgstr
            
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World'})
