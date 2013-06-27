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

    def test_unique_last(self):
        options = optparse.Values({'best': False, 'sort': False})
        options, args = pounique.parse_options([self.pf1, self.pf2], options)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique())
        
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
        options = optparse.Values({'best': True, 'sort': False})
        options, args = pounique.parse_options([self.pf1, self.pf2], options)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique())
        
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
        options = optparse.Values({'best': False, 'sort': True})
        options, args = pounique.parse_options([self.pf1, self.pf2], options)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique())
        self.assertEquals(
            [x.msgid for x in entries], 
            [u'Baz', u'bazoo', u'Hello World', u'label_bar', u'label_foo'])
