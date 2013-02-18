import unittest
import os
from potools import podiff

class TestPodiff(unittest.TestCase):
    """ """

    def setUp(self):
        self.pot = open(os.getcwd()+'/../../potools/tests/locales/test.pot')
        self.po1 = open(os.getcwd()+'/../../potools/tests/locales/nl_test.po')
        self.po2 = open(os.getcwd()+'/../../potools/tests/locales/nl_test2.po')
        self.podiff = podiff.Podiff()

    def test_podiff(self):
        """ """
        # Diff po file with itself.
        diff = self.podiff._diff(
                        os.getcwd()+'/../../potools/tests/locales/nl_test.po', 
                        os.getcwd()+'/../../potools/tests/locales/nl_test.po')
        self.assertEquals(len(diff), 0)

        # Diff po file with another file.
        diff = self.podiff._diff(
                        os.getcwd()+'/../../potools/tests/locales/nl_test.po', 
                        os.getcwd()+'/../../potools/tests/locales/nl_test2.po')
        self.assertEquals(len(diff), 6)

