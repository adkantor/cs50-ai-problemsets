import unittest
import os
import string
import nltk
import math

import questions


class LoadFilesTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.corpus_dir = 'corpus'
        cls.result = questions.load_files('corpus')
        cls.filenames = os.listdir('corpus')

    def test_return_type_is_dictionary(self):
        self.assertIsInstance(self.result, dict)

    def test_dictionary_keys_are_filenames(self):
        self.assertEqual(len(self.filenames), len(self.result))
        for filename in self.result.keys():
            with self.subTest(filename=filename):
                self.assertIn(filename, self.filenames)

    def test_dictionary_values_are_non_empty_strings(self):
        for content in self.result.values():
            with self.subTest(content=content):
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 0)

# End class


class TokenizeTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.document = """
        If someone in the games has a "threat" (that is, two in a row), take the remaining square. In March 2016, AlphaGo won 4 out of 5 games.
        """
        cls.result = questions.tokenize(cls.document)
        cls.tokens = [
            'someone', 'games', '``', 'threat', "''", 'two', 'row', 'take', 'remaining', 'square',
            'march', '2016', 'alphago', '4', '5', 'games'] # the word 'won' is filtered by nltk.corpus.stopwords!

    def test_return_type_is_list(self):
        self.assertIsInstance(self.result, list)

    def test_output_excludes_punctuation(self):
        for token in self.result:
            with self.subTest(token=token):
                self.assertNotIn(token, string.punctuation)

    def test_output_excludes_stopwords(self):
        for token in self.result:
            with self.subTest(token=token):
                self.assertNotIn(token, nltk.corpus.stopwords.words('english'))

    def test_output_contains_all_important_words_in_order(self):
        self.assertListEqual(self.result, self.tokens)

# End class


class ComputeIdfsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.documents = {
            'x': ['a', 'b', 'c'],
            'y': ['c', 'd', 'e'],
            'z': ['e', 'f', 'c'],            
        }
        cls.words = set(['a', 'b', 'c', 'd', 'e', 'f'])
        cls.result = questions.compute_idfs(cls.documents)

    def test_get_words(self):
        words = questions.get_words(self.documents)
        self.assertIsInstance(words, set)
        self.assertSetEqual(self.words, words)

    def test_return_type_is_dictionary(self):
        self.assertIsInstance(self.result, dict)

    def test_output_is_correct(self):
        expected = {
            'a': math.log(3 / 1),
            'b': math.log(3 / 1),
            'c': math.log(3 / 3),
            'd': math.log(3 / 1),
            'e': math.log(3 / 2),
            'f': math.log(3 / 1),
        }
        self.assertDictEqual(self.result, expected)

# End class


class TopFilesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.query = set(['a', 'b', 'c'])
        cls.files = {
            'x': ['a', 'b', 'c'],
            'y': ['c', 'b', 'e'],
            'z': ['e', 'f', 'c'],            
        }
        cls.idfs = {
            'a': math.log(3 / 1),
            'b': math.log(3 / 1),
            'c': math.log(3 / 3),
            'd': math.log(3 / 1),
            'e': math.log(3 / 2),
            'f': math.log(3 / 1),
        }

    def test_compute_tfidfs(self):
        result = questions.compute_sum_tfidfs(self.query, self.files, self.idfs)
        expected = {
            'x': 1 * self.idfs['a'] + 1 * self.idfs['b'] + 1 * self.idfs['c'],
            'y': 0 * self.idfs['a'] + 1 * self.idfs['b'] + 1 * self.idfs['c'],
            'z': 0 * self.idfs['a'] + 0 * self.idfs['b'] + 1 * self.idfs['c'],                 
        }
        self.assertDictEqual(result, expected)

    def test_compute_tfidfs_handles_unknown_query_terms(self):
        query = set(['a', 'b', 'c', 'foo', 'bar'])
        result = questions.compute_sum_tfidfs(query, self.files, self.idfs)
        expected = {
            'x': 1 * self.idfs['a'] + 1 * self.idfs['b'] + 1 * self.idfs['c'],
            'y': 0 * self.idfs['a'] + 1 * self.idfs['b'] + 1 * self.idfs['c'],
            'z': 0 * self.idfs['a'] + 0 * self.idfs['b'] + 1 * self.idfs['c'],                 
        }
        self.assertDictEqual(result, expected)

    def test_return_type_is_list(self):
        result = questions.top_files(self.query, self.files, self.idfs, 1)
        self.assertIsInstance(result, list)

    def test_output_length(self):
        for n in range(1, 4):
            with self.subTest(n=n):
                result = questions.top_files(self.query, self.files, self.idfs, n)
                self.assertEqual(len(result), n)

    def test_output_is_correct(self):
        # (n, expected)
        cases = [
            (1, ['x']),
            (2, ['x', 'y']),
            (3, ['x', 'y', 'z']),
        ]
        for n, expected in cases:
            with self.subTest(n=n, cases=cases):
                result = questions.top_files(self.query, self.files, self.idfs, n)
                self.assertListEqual(result, expected)

# End class


class TopSentencesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.query = set(['a', 'b', 'c'])
        cls.sentences = {
            'abcde': ['a', 'b', 'c', 'd', 'e'],
            'cbefg': ['c', 'b', 'e', 'f', 'g'],
            'aghia': ['a', 'g', 'h', 'i', 'a'],            
        }
        cls.idfs = {
            'a': 0.5,
            'b': 0.5,
            'c': 0,
            'd': 0.2,
            'e': 1.2,
            'f': 0.8,
            'g': 0,
            'h': 0.3,
            'i': 1.6,
        }

    def test_compute_mwm_qtd(self):
        result = questions.compute_mwm_qtd(self.query, self.sentences, self.idfs)
        expected = {
            'abcde': (0.5 + 0.5 + 0, 3/5),
            'cbefg': (0 + 0.5 + 0, 2/5),
            'aghia': (0 + 0.5 + 0, 1/5),                 
        }
        self.assertDictEqual(result, expected)

    def test_compute_mwm_qtd_handles_unknown_query_terms(self):
        query = set(['a', 'b', 'c', 'foo', 'bar'])
        result = questions.compute_mwm_qtd(query, self.sentences, self.idfs)
        expected = {
            'abcde': (0.5 + 0.5 + 0, 3/5),
            'cbefg': (0 + 0.5 + 0, 2/5),
            'aghia': (0 + 0.5 + 0, 1/5),                 
        }
        self.assertDictEqual(result, expected)

    def test_return_type_is_list(self):
        result = questions.top_sentences(self.query, self.sentences, self.idfs, 1)
        self.assertIsInstance(result, list)

    def test_output_length(self):
        for n in range(1, 4):
            with self.subTest(n=n):
                result = questions.top_sentences(self.query, self.sentences, self.idfs, n)
                self.assertEqual(len(result), n)

    def test_output_is_correct(self):
        # (n, expected)
        cases = [
            (1, ['abcde']),
            (2, ['abcde', 'cbefg']),
            (3, ['abcde', 'cbefg', 'aghia']),
        ]
        for n, expected in cases:
            with self.subTest(n=n, cases=cases):
                result = questions.top_sentences(self.query, self.sentences, self.idfs, n)
                self.assertListEqual(result, expected)

# End class


def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(LoadFilesTestCase('test_return_type_is_dictionary'))
    suite.addTest(LoadFilesTestCase('test_dictionary_keys_are_filenames'))
    suite.addTest(LoadFilesTestCase('test_dictionary_values_are_non_empty_strings'))
    
    suite.addTest(TokenizeTestCase('test_return_type_is_list'))
    suite.addTest(TokenizeTestCase('test_output_excludes_punctuation'))
    suite.addTest(TokenizeTestCase('test_output_excludes_stopwords'))
    suite.addTest(TokenizeTestCase('test_output_contains_all_important_words_in_order'))
    
    suite.addTest(ComputeIdfsTestCase('test_get_words'))
    suite.addTest(ComputeIdfsTestCase('test_return_type_is_dictionary'))
    suite.addTest(ComputeIdfsTestCase('test_output_is_correct'))
    
    suite.addTest(TopFilesTestCase('test_compute_tfidfs'))
    suite.addTest(TopFilesTestCase('test_compute_tfidfs_handles_unknown_query_terms'))
    suite.addTest(TopFilesTestCase('test_return_type_is_list'))
    suite.addTest(TopFilesTestCase('test_output_length'))
    suite.addTest(TopFilesTestCase('test_output_is_correct'))
    
    suite.addTest(TopSentencesTestCase('test_compute_mwm_qtd'))
    suite.addTest(TopSentencesTestCase('test_return_type_is_list'))
    suite.addTest(TopSentencesTestCase('test_output_length'))
    suite.addTest(TopSentencesTestCase('test_output_is_correct'))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
