import unittest
from copy import deepcopy

from minesweeper import Sentence, MinesweeperAI


class SentenceTestCase(unittest.TestCase):
    
    def test_known_mines(self):        
        cells = [(0,1), (1,0), (1,1)]
        counts = [3, 2, 1, 0]
        expected_results = [set(cells), set(), set(), set()]
        
        for count, expected_result in zip(counts, expected_results):
            with self.subTest(count=count, expected_result=expected_result):
                s = Sentence(cells, count)
                known_mines = s.known_mines()
                self.assertSetEqual(known_mines, expected_result)

    def test_known_safes(self):        
        cells = [(0,1), (1,0), (1,1)]
        counts = [3, 2, 1, 0]
        expected_results = [set(), set(), set(), set(cells)]
        
        for count, expected_result in zip(counts, expected_results):
            with self.subTest(count=count, expected_result=expected_result):
                s = Sentence(cells, count)
                known_safes = s.known_safes()
                self.assertSetEqual(known_safes, expected_result)

    def test_mark_mine(self):        
        cells = [(0,1), (1,0), (1,1)]
        count = 2

        s = Sentence(cells, count)
        mine_cell = (1,1)
        s.mark_mine(mine_cell)

        self.assertSetEqual(s.cells, set([(0,1), (1,0)]))
        self.assertEqual(s.count, 1)

    def test_mark_mine_cell_is_not_in_sentence(self):        
        cells = [(0,1), (1,0), (1,1)]
        count = 2

        s = Sentence(cells, count)
        mine_cell = (2,1)
        s.mark_mine(mine_cell)

        self.assertSetEqual(s.cells, set(cells))
        self.assertEqual(s.count, count)

    def test_mark_mine_last_cell(self):        
        cells = [(0,1)]
        count = 1

        s = Sentence(cells, count)
        mine_cell = (0,1)
        s.mark_mine(mine_cell)

        self.assertSetEqual(s.cells, set())
        self.assertEqual(s.count, 0)

    def test_mark_safe(self):        
        cells = [(0,1), (1,0), (1,1)]
        count = 2

        s = Sentence(cells, count)
        safe_cell = (1,1)
        s.mark_safe(safe_cell)

        self.assertSetEqual(s.cells, set([(0,1), (1,0)]))
        self.assertEqual(s.count, 2)

    def test_mark_safe_cell_is_not_in_sentence(self):        
        cells = [(0,1), (1,0), (1,1)]
        count = 2

        s = Sentence(cells, count)
        safe_cell = (2,1)
        s.mark_safe(safe_cell)

        self.assertSetEqual(s.cells, set(cells))
        self.assertEqual(s.count, count)

    def test_mark_safe_last_cell(self):        
        cells = [(0,1)]
        count = 0

        s = Sentence(cells, count)
        safe_cell = (0,1)
        s.mark_safe(safe_cell)

        self.assertSetEqual(s.cells, set())
        self.assertEqual(s.count, 0)

# End class


class MinesweeperAITestCase(unittest.TestCase):

    def test_add_current_move_to_empty_knowledge_base(self):
        ai = MinesweeperAI(3, 3)
        cell = (1,1)
        count = 1
        ai.add_current_move_to_knowledge_base(cell, count)

        self.assertEqual(len(ai.knowledge), 1)
        self.assertIsInstance(ai.knowledge[0], Sentence)
        self.assertEqual(ai.knowledge[0].cells, {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)})
        self.assertEqual(ai.knowledge[0].count, count)

    def test_add_current_move_to_nonempty_knowledge_base(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [Sentence({(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}, 1)]
        cell = (0,0)
        count = 0
        ai.add_current_move_to_knowledge_base(cell, count)

        self.assertEqual(len(ai.knowledge), 2)
        for sentence in ai.knowledge:
            self.assertIsInstance(sentence, Sentence)
        self.assertEqual(ai.knowledge[1].cells, {(0, 1), (1, 0), (1, 1)})
        self.assertEqual(ai.knowledge[1].count, count)

    def test_update_safes(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [Sentence({(0, 1), (1, 0), (1, 1)}, 0)]
        result = ai.update_safes()

        self.assertSetEqual(ai.safes, {(0, 1), (1, 0), (1, 1)})
        self.assertTrue(result)
        self.assertSetEqual(ai.knowledge[0].cells, set())

    def test_update_safes_nochange(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [Sentence({(0, 1), (1, 0), (1, 1)}, 0)]
        ai.safes = {(0, 1), (1, 0), (1, 1)}
        result = ai.update_safes()

        self.assertSetEqual(ai.safes, {(0, 1), (1, 0), (1, 1)})
        self.assertFalse(result)
        self.assertSetEqual(ai.knowledge[0].cells, {(0, 1), (1, 0), (1, 1)})

    def test_update_mines(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [Sentence({(0, 1), (1, 0), (1, 1)}, 3)]
        result = ai.update_mines()

        self.assertSetEqual(ai.mines, {(0, 1), (1, 0), (1, 1)})
        self.assertTrue(result)
        self.assertSetEqual(ai.knowledge[0].cells, set())

    def test_update_mines_nochange(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [Sentence({(0, 1), (1, 0), (1, 1)}, 3)]
        ai.mines = {(0, 1), (1, 0), (1, 1)}
        result = ai.update_mines()

        self.assertSetEqual(ai.mines, {(0, 1), (1, 0), (1, 1)})
        self.assertFalse(result)
        self.assertSetEqual(ai.knowledge[0].cells, {(0, 1), (1, 0), (1, 1)})

    def test_cleanup_knowledge_single(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [
            Sentence({(0, 1), (1, 0), (1, 1)}, 3), 
            Sentence({}, 0)
        ]
        self.assertEqual(len(ai.knowledge), 2)
        ai.cleanup_knowledge()  
        self.assertEqual(len(ai.knowledge), 1)

    def test_cleanup_knowledge_multiple(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [
            Sentence({(0, 1), (1, 0), (1, 1)}, 3), 
            Sentence({}, 0), 
            Sentence({}, 0)
        ]
        self.assertEqual(len(ai.knowledge), 3)
        ai.cleanup_knowledge()  
        self.assertEqual(len(ai.knowledge), 1)

    def test_cleanup_knowledge_none(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [
            Sentence({(0, 1), (1, 0), (1, 1)}, 3), 
            Sentence({(1, 1), (2, 0), (2, 1)}, 3)
        ]
        self.assertEqual(len(ai.knowledge), 2)
        ai.cleanup_knowledge()  
        self.assertEqual(len(ai.knowledge), 2)

    def test_infer_new_sentences_success(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [
            Sentence({(1, 0), (1, 1), (1, 2)}, 1), 
            Sentence({(2, 0), (1, 0), (1, 1), (1, 2), (2, 2)}, 2)
        ]
        expected = Sentence({(2, 0), (2, 2)}, 1)
        result = ai.infer_new_sentences()

        self.assertEqual(len(ai.knowledge), 3)
        self.assertTrue(result)
        self.assertEqual(ai.knowledge[2].cells, expected.cells)
        self.assertEqual(ai.knowledge[2].count, expected.count)

    def test_infer_new_sentences_unsuccessful_1(self):
        ai = MinesweeperAI(3, 3)
        ai.knowledge = [
            Sentence({(1, 0), (1, 1), (1, 2)}, 1), 
            Sentence({(1, 0), (1, 1), (1, 2)}, 1)
        ]
        result = ai.infer_new_sentences()

        self.assertEqual(len(ai.knowledge), 2)
        self.assertFalse(result)

    def test_make_safe_move_returns_valid_cell_if_one_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1), (1,0)}
        ai.safes = {(0,0), (0,1), (1,0), (1,1)}
        expected = (1,1)
        result = ai.make_safe_move() 

        self.assertEqual(result, expected) 

    def test_make_safe_move_returns_valid_cell_if_multiple_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1)}
        ai.safes = {(0,0), (0,1), (1,0), (1,1)}
        expected = [(1,0), (1,1)]
        result = ai.make_safe_move() 

        self.assertIn(result, expected) 

    def test_make_safe_move_returns_none_if_none_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1), (1,0)}
        ai.safes = {(0,0), (0,1), (1,0)}
        result = ai.make_safe_move() 

        self.assertIsNone(result)

    def test_make_random_move_returns_valid_cell_if_one_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)}
        ai.mines = {(2,0), (2,1)}
        expected = (2,2)
        result = ai.make_random_move() 

        self.assertEqual(result, expected) 

    def test_make_random_move_returns_valid_cell_if_multiple_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1)}
        ai.mines = {(2,0), (2,1)}
        expected = [(0,2), (1,0), (1,1), (1,2), (2,2)]
        result = ai.make_random_move()

        self.assertIn(result, expected) 

    def test_make_random_move_returns_none_if_none_available(self):
        ai = MinesweeperAI(3, 3)
        ai.moves_made = {(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)}
        ai.mines = {(2,0), (2,1), (2,2)}
        result = ai.make_random_move() 

        self.assertIsNone(result)


# End class


def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(SentenceTestCase('test_known_mines'))
    suite.addTest(SentenceTestCase('test_known_safes'))
    suite.addTest(SentenceTestCase('test_mark_mine'))
    suite.addTest(SentenceTestCase('test_mark_mine_cell_is_not_in_sentence'))
    suite.addTest(SentenceTestCase('test_mark_mine_last_cell'))
    suite.addTest(SentenceTestCase('test_mark_safe'))
    suite.addTest(SentenceTestCase('test_mark_safe_cell_is_not_in_sentence'))
    suite.addTest(SentenceTestCase('test_mark_safe_last_cell'))

    suite.addTest(MinesweeperAITestCase('test_add_current_move_to_empty_knowledge_base'))
    suite.addTest(MinesweeperAITestCase('test_add_current_move_to_nonempty_knowledge_base'))
    suite.addTest(MinesweeperAITestCase('test_update_safes'))
    suite.addTest(MinesweeperAITestCase('test_update_safes_nochange'))
    suite.addTest(MinesweeperAITestCase('test_update_mines'))
    suite.addTest(MinesweeperAITestCase('test_update_mines_nochange'))
    suite.addTest(MinesweeperAITestCase('test_cleanup_knowledge_single'))
    suite.addTest(MinesweeperAITestCase('test_cleanup_knowledge_multiple'))
    suite.addTest(MinesweeperAITestCase('test_cleanup_knowledge_none'))
    suite.addTest(MinesweeperAITestCase('test_infer_new_sentences_success'))
    suite.addTest(MinesweeperAITestCase('test_infer_new_sentences_unsuccessful_1'))
    suite.addTest(MinesweeperAITestCase('test_make_safe_move_returns_valid_cell_if_one_available'))
    suite.addTest(MinesweeperAITestCase('test_make_safe_move_returns_valid_cell_if_multiple_available'))
    suite.addTest(MinesweeperAITestCase('test_make_safe_move_returns_none_if_none_available'))
    suite.addTest(MinesweeperAITestCase('test_make_random_move_returns_valid_cell_if_one_available'))
    suite.addTest(MinesweeperAITestCase('test_make_random_move_returns_valid_cell_if_multiple_available'))
    suite.addTest(MinesweeperAITestCase('test_make_random_move_returns_none_if_none_available'))
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
