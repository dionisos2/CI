import unittest
import sys
#from proboscis import test # maybe we should use it for adding dependencies between test

sys.path.append("..")

from CI_list import *

class CI_listTestCase(unittest.TestCase):

    def setUp(self):
        self.ci1 = CI("ci1")
        self.ci2 = CI("ci2")
        self.ci3 = CI("ci3")
        self.ci_list = CI_list([self.ci1, self.ci2])

    def test_append(self):
        self.ci_list.append(self.ci3)
        self.assertEqual(self.ci_list.get_list_of_ci(), [self.ci1, self.ci2, self.ci3])

    def test_iter(self):
        for (have, want) in zip(self.ci_list, [self.ci1, self.ci2]):
            with self.subTest(i=(have, want)):
                self.assertEqual(have, want)

    def test_find(self):
        self.assertEqual(self.ci_list.find("ci2"), self.ci2)
        self.assertEqual(self.ci_list.find("unknow"), None)

    def test_load_xml(self):
        self.ci_list.load_xml("ci.xml")
        self.assertEqual(len(self.ci_list), 5)
        ci_1 = self.ci_list.find("ci_1")
        ci_2 = self.ci_list.find("ci_2")
        ci_3 = self.ci_list.find("ci_3")
        ci_4 = self.ci_list.find("ci_4")
        ci_5 = self.ci_list.find("ci_5")
        list_of_ci = [ci_1, ci_2, ci_3, ci_4, ci_5]

        for (i, ci) in zip(range(1, len(list_of_ci)+1), list_of_ci):
            with self.subTest(i=i):
                self.assertEqual(ci.get_url(), "url"+str(i))

        self.assertEqual(ci_1.get_children(), [])
        self.assertEqual(ci_2.get_children(), [])
        self.assertEqual(ci_3.get_children(), [ci_2])
        self.assertEqual(ci_4.get_children(), [ci_1, ci_3])
        self.assertEqual(ci_5.get_children(), [ci_1, ci_2])
