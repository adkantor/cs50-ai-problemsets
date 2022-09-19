import unittest

import pagerank as pr


class TransitionModelTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus0 = pr.crawl('corpus0')
        cls.corpus1 = pr.crawl('corpus1')
        cls.corpus2 = pr.crawl('corpus2')
        cls.corpus3 = {
            "1.html": {"2.html", "3.html"}, 
            "2.html": {"3.html"}, 
            "3.html": {"2.html"}
        }

    def test_no_outgoing_link(self):
        corpus = self.corpus2
        page = "recursion.html"
        
        result = pr.transition_model(corpus, page, 0.85)

        # result is dictionary
        self.assertIsInstance(result, dict)
        # result returns even distribution to all pages
        expected = {
            'ai.html': 1/8,
            'algorithms.html': 1/8,
            'c.html': 1/8,
            'inference.html': 1/8,
            'logic.html': 1/8,
            'programming.html': 1/8,
            'python.html': 1/8,
            'recursion.html': 1/8      
        }
        for r, e in zip(result.values(), expected.values()):
            with self.subTest(r=r, e=e):
                self.assertAlmostEqual(r, e)

    def test_one_outgoing_link(self):
        corpus = self.corpus0
        page = "1.html"
        
        result = pr.transition_model(corpus, page, 0.85)

        # result is dictionary
        self.assertIsInstance(result, dict)
        # result returns even distribution to all pages
        expected = {
            '1.html': (0.15 * 1/4), 
            '2.html': (0.85 * 1) + (0.15 * 1/4), 
            '3.html': (0.15 * 1/4), 
            '4.html': (0.15 * 1/4)       
        }
        for r, e in zip(result.values(), expected.values()):
            with self.subTest(r=r, e=e):
                self.assertAlmostEqual(r, e)

    def test_multiple_outgoing_links(self):
        corpus = self.corpus0
        page = "2.html"
        
        result = pr.transition_model(corpus, page, 0.85)

        # result is dictionary
        self.assertIsInstance(result, dict)
        # result returns even distribution to all pages
        expected = {
            '1.html': (0.85 * 1/2) + (0.15 * 1/4), 
            '2.html': (0.15 * 1/4), 
            '3.html': (0.85 * 1/2) + (0.15 * 1/4), 
            '4.html': (0.15 * 1/4)       
        }
        for r, e in zip(result.values(), expected.values()):
            with self.subTest(r=r, e=e):
                self.assertAlmostEqual(r, e)

# End class

class SamplePagerankTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus0 = pr.crawl('corpus0')
        cls.corpus1 = pr.crawl('corpus1')
        cls.corpus2 = pr.crawl('corpus2')
        cls.corpus3 = {
            "1.html": {"2.html", "3.html"}, 
            "2.html": {"3.html"}, 
            "3.html": {"2.html"}
        }

    def test_function_returns_dictionary(self):
        corpuses = [self.corpus0, self.corpus1, self.corpus2, self.corpus3]

        for corpus in corpuses:
            with self.subTest(corpus=corpus):
                rank = pr.sample_pagerank(corpus, 0.85, 1000)
                self.assertIsInstance(rank, dict)

    def test_ranks_sum_up_to_one(self):
        corpuses = [self.corpus0, self.corpus1, self.corpus2, self.corpus3]

        for corpus in corpuses:
            with self.subTest(corpus=corpus):
                rank = pr.sample_pagerank(corpus, 0.85, 10000)
                values = list(rank.values())
                self.assertAlmostEqual(sum(values), 1)

# End class

class IteratePagerankTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus0 = pr.crawl('corpus0')
        cls.corpus1 = pr.crawl('corpus1')
        cls.corpus2 = pr.crawl('corpus2')
        cls.corpus3 = {
            "1.html": {"2.html", "3.html"}, 
            "2.html": {"3.html"}, 
            "3.html": {"2.html"}
        }

    def test_get_page_rank_first_iteration(self):
        # [corpus, page, expected_page_rank[]
        cases = [
            [self.corpus0, "1.html", 0.14375],  # 0.15/4 + 0.85*(0.25/2)
            [self.corpus0, "2.html", 0.56875],  # 0.15/4 + 0.85*(0.25/1 + 0.25/2 + 0.25/1)
            [self.corpus0, "3.html", 0.14375],  # 0.15/4 + 0.85*(0.25/2)
            [self.corpus0, "4.html", 0.14375],  # 0.15/4 + 0.85*(0.25/2)            
            [self.corpus2, "ai.html",           0.19140625],  # 0.15/8 + 0.85*(0.125/1 + 0.125/2 + 0,125/8)
            [self.corpus2, "algorithms.html",   0.08515625],  # 0.15/8 + 0.85*(0.125/2 + 0,125/8)
            [self.corpus2, "c.html",            0.08515625],  # 0.15/8 + 0.85*(0.125/2 + 0,125/8)
            [self.corpus2, "inference.html",    0.19140625],  # 0.15/8 + 0.85*(0.125/1 + 0.125/2 + 0,125/8)
            [self.corpus2, "logic.html",        0.03203125],  # 0.15/8 + 0.85*(0,125/8)
            [self.corpus2, "programming.html",  0.24453125],  # 0.15/8 + 0.85*(0.125/2 + 0.125/1 + 0.125/2 + 0,125/8)
            [self.corpus2, "python.html",       0.08515625],  # 0.15/8 + 0.85*(0.125/2 + 0,125/8)
            [self.corpus2, "recursion.html",    0.08515625],  # 0.15/8 + 0.85*(0.125/2 + 0,125/8)
            
        ]

        for case in cases:
            corpus, page, expected_page_rank = case
            with self.subTest(corpus=corpus, page=page, expected_page_rank=expected_page_rank):
                amended_corpus = pr.get_amended_corpus(corpus)
                N = len(amended_corpus)
                current_rank = dict.fromkeys(amended_corpus.keys(), 1/N)
                result = pr.get_page_rank(page, amended_corpus, current_rank, 0.85)
                self.assertAlmostEqual(result, expected_page_rank, places=4)

    def test_function_returns_dictionary(self):
        corpuses = [self.corpus0, self.corpus1, self.corpus2, self.corpus3]

        for corpus in corpuses:
            with self.subTest(corpus=corpus):
                rank = pr.iterate_pagerank(corpus, 0.85)
                self.assertIsInstance(rank, dict)

    def test_ranks_sum_up_to_one(self):
        corpuses = [self.corpus0, self.corpus1, self.corpus2, self.corpus3]

        for corpus in corpuses:
            with self.subTest(corpus=corpus):
                rank = pr.iterate_pagerank(corpus, 0.85)
                values = list(rank.values())
                self.assertAlmostEqual(sum(values), 1)

# End class


def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(TransitionModelTestCase('test_no_outgoing_link'))
    suite.addTest(TransitionModelTestCase('test_one_outgoing_link'))
    suite.addTest(TransitionModelTestCase('test_multiple_outgoing_links'))

    suite.addTest(SamplePagerankTestCase('test_function_returns_dictionary'))
    suite.addTest(SamplePagerankTestCase('test_ranks_sum_up_to_one'))

    suite.addTest(IteratePagerankTestCase('test_get_page_rank_first_iteration')) 
    suite.addTest(IteratePagerankTestCase('test_function_returns_dictionary'))        
    suite.addTest(IteratePagerankTestCase('test_ranks_sum_up_to_one'))        
          
        
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())


# corpus0
# {
# '1.html': {'2.html'}, 
# '2.html': {'1.html', '3.html'}, 
# '3.html': {'2.html', '4.html'}, 
# '4.html': {'2.html'}
# }


# corpus1
# {
# 'bfs.html': {'search.html'}, 
# 'dfs.html': {'bfs.html', 'search.html'}, 
# 'games.html': {'minesweeper.html', 'tictactoe.html'}, 
# 'minesweeper.html': {'games.html'}, 
# 'minimax.html': {'games.html', 'search.html'}, 
# 'search.html': {'bfs.html', 'dfs.html', 'minimax.html'}, 
# 'tictactoe.html': {'games.html', 'minimax.html'}
# }


# corpus2
# {
# 'ai.html': {'inference.html', 'algorithms.html'}, 
# 'algorithms.html': {'programming.html', 'recursion.html'}, 
# 'c.html': {'programming.html'}, 
# 'inference.html': {'ai.html'}, 
# 'logic.html': {'inference.html'}, 
# 'programming.html': {'python.html', 'c.html'}, 
# 'python.html': {'ai.html', 'programming.html'}, 
# 'recursion.html': set()
# }