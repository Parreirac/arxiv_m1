import unittest

import ExtractDataFromPDF


class TestApp(unittest.TestCase):



    def test_1(self):
        rv_creator, rv_producer, rv_subtitle, rv_keywords, rv_reference_list, rv_reference_ctrl_set = ExtractDataFromPDF("./Files/1001.4892.pdf")
        self.assertEqual(rv_keywords,'Ontology, XML Mining, Application Integration.')
