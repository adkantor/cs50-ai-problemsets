import unittest
from unittest.mock import Mock
from unittest.mock import patch

from crossword import Crossword, Variable
import generate

class CrosswordCreatorTestCase(unittest.TestCase):
    
    def test_enforce_node_consistency(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 2
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable)
        mock_variable3.length = 5
        mock_variable4 = Mock(spec=Variable)
        mock_variable4.length = 7
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.words = {"A", "AA", "AAA", "AAAA", "AAAAA", "BBBBB"}
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3, mock_variable4}
        cc = generate.CrosswordCreator(mock_crossword)
        cc.enforce_node_consistency()

        expected = {
            mock_variable1: {"AA"},
            mock_variable2: {"AAA"},
            mock_variable3: {"AAAAA", "BBBBB"},
            mock_variable4: set()
        }
        self.assertDictEqual(cc.domains, expected)
    

    def test_words_to_remove_unfiltered(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "CCC", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        cc = generate.CrosswordCreator(mock_crossword)
        cases = [
            ({mock_variable1: {"ABA", "BAB"}, mock_variable2: {"AAA", "CCC"}}, {"ABA"}),
            ({mock_variable1: {"ABA", "CDC"}, mock_variable2: {"AAA", "BBB"}}, {"CDC"}),
            ({mock_variable1: {"ABA", "CBC"}, mock_variable2: {"AAA", "BBB"}}, set()),
        ]
        
        for domains, expected in cases:
            with self.subTest(domains=domains, expected=expected):
                cc.domains = domains
                result = cc.get_words_to_remove(mock_variable1, mock_variable2)
                self.assertSetEqual(result, expected)


    def test_words_to_remove_filtered(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "CCC", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        cc = generate.CrosswordCreator(mock_crossword)
        cases = [
            ({mock_variable1: {"ABA", "BAB"}, mock_variable2: {"AAA", "CCC"}}, "AAA", {"ABA"}),
            ({mock_variable1: {"ABA", "BAB"}, mock_variable2: {"AAA", "CCC"}}, "CCC", {"ABA", "BAB"}),
            ({mock_variable1: {"ABA", "CDC"}, mock_variable2: {"AAA", "BBB"}}, "AAA", {"ABA", "CDC"}),
            ({mock_variable1: {"ABA", "CDC"}, mock_variable2: {"AAA", "BBB"}}, "BBB", {"CDC"}),
            ({mock_variable1: {"ABA", "CBC"}, mock_variable2: {"AAA", "BBB"}}, "AAA", {"ABA", "CBC"}),
            ({mock_variable1: {"ABA", "CBC"}, mock_variable2: {"AAA", "BBB"}}, "BBB", set()),
        ]
        
        for domains, filter_word, expected in cases:
            with self.subTest(domains=domains, filter_word=filter_word, expected=expected):
                cc.domains = domains
                result = cc.get_words_to_remove(mock_variable1, mock_variable2, filter_word)
                self.assertSetEqual(result, expected)


    def test_revise_returns_false_if_no_overlap(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "BBB", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = None
        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"ABA", "BAB"},
            mock_variable2: {"AAA", "BBB"},
        }
        result = cc.revise(mock_variable1, mock_variable2)
        self.assertFalse(result)
        

    def test_revise_if_overlap_and_revised(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "CCC", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"ABA", "BAB"},
            mock_variable2: {"AAA", "CCC"},
        }
        expected = {
            mock_variable1: {"BAB"},
            mock_variable2: {"AAA", "CCC"},
        }
        result = cc.revise(mock_variable1, mock_variable2)
        
        # function returns True
        self.assertTrue(result)
        # function updates domain: "ABA" removed
        self.assertDictEqual(cc.domains, expected)
    

    def test_revise_if_overlap_and_not_revised(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "BBB", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"ABA", "BAB"},
            mock_variable2: {"AAA", "BBB"},
        }
        expected = {
            mock_variable1: {"ABA", "BAB"},
            mock_variable2: {"AAA", "BBB"},
        }
        result = cc.revise(mock_variable1, mock_variable2)
        
        # function returns False
        self.assertFalse(result)
        # function does not update domain
        self.assertDictEqual(cc.domains, expected)


    def test_ac3(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {}
        mock_crossword.words = {}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        mock_crossword.neighbors.return_value = {mock_variable2}
        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"ABA", "BAB"},
            mock_variable2: {"AAA", "CCC"},
        }
        expected = {
            mock_variable1: {"BAB"},
            mock_variable2: {"AAA", "CCC"},
        }
        result = cc.ac3()

        self.assertTrue(result)
        self.assertDictEqual(cc.domains, expected)


    def test_assignment_complete_returns_true_if_complete(self):
        self.maxDiff = None
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {'var1', 'var2', 'var3'}
        mock_crossword.words = {}
        cc = generate.CrosswordCreator(mock_crossword)
        assignment = {
            'var1': 'ABCD',
            'var2': 'EFGH',
            'var3': 'IJK'
        }
        result = cc.assignment_complete(assignment)

        self.assertTrue(result)


    def test_assignment_complete_returns_false_if_incomplete(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable)
        mock_variable3.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {}
        cc = generate.CrosswordCreator(mock_crossword)
        assignments = [
            {'var2': 'EFGH', 'var3': 'IJK'},
            {'var1': 'ABCD', 'var3': 'IJK'},
            {'var1': 'ABCD', 'var2': 'EFGH'},
            {'var1': 'ABCD'},
            {'var2': 'EFGH'},
            {'var3': 'IJK'},
            {},
        ]

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.assignment_complete(assignment)
                self.assertFalse(result)


    def test_consistent_returns_false_if_not_distinct(self):
        self.maxDiff = None
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {}
        mock_crossword.words = {}
        cc = generate.CrosswordCreator(mock_crossword)
        assignments = [
            {'var1': 'ABCD', 'var2': 'ABCD', 'var3': 'IJK'},
            {'var1': 'ABCD', 'var2': 'EFGH', 'var3': 'ABCD'},
            {'var1': 'ABCD', 'var2': 'EFGH', 'var3': 'EFGH'},
        ]

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.consistent(assignment)
                self.assertFalse(result)


    def test_assignment_complete_returns_false_if_incorrect_length(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable)
        mock_variable3.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {}
        cc = generate.CrosswordCreator(mock_crossword)
        assignments = [
            {mock_variable1: 'ABCD', mock_variable2: 'EFG', mock_variable3: 'IJK'},
            {mock_variable1: 'ABC', mock_variable2: 'EFGH', mock_variable3: 'IJK'},
            {mock_variable1: 'ABC', mock_variable2: 'EFG', mock_variable3: 'IJKL'},
            {mock_variable1: 'ABCD', mock_variable2: 'EFGH', mock_variable3: 'IJK'},
            {mock_variable1: 'ABC', mock_variable2: 'EFGH', mock_variable3: 'IJKL'},
            {mock_variable1: 'ABCD', mock_variable2: 'EFG', mock_variable3: 'IJKL'},
            {mock_variable1: 'ABCD', mock_variable2: 'EFGH', mock_variable3: 'IJKL'},            
        ]

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.consistent(assignment)
                self.assertFalse(result)


    def test_assignment_complete_returns_false_if_conflicts_neighbor(self):
                
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        mock_crossword.overlaps[mock_variable2, mock_variable1] = (1, 1)
        
        def side_effect(value):
            if value == mock_variable1: 
                return {mock_variable2}
            elif value == mock_variable2: 
                return {mock_variable1}

        mock_crossword.neighbors.side_effect = side_effect

        cc = generate.CrosswordCreator(mock_crossword)
        assignments = [
            {mock_variable1: 'ABC', mock_variable2: 'EFG'},
        ]

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.consistent(assignment)
                self.assertFalse(result)


    def test_assignment_complete(self):                
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        mock_crossword.overlaps[mock_variable2, mock_variable1] = (1, 1)
        
        def side_effect(value):
            if value == mock_variable1: 
                return {mock_variable2}
            elif value == mock_variable2: 
                return {mock_variable1}

        mock_crossword.neighbors.side_effect = side_effect

        cc = generate.CrosswordCreator(mock_crossword)
        assignments = [
            {mock_variable1: 'ABC', mock_variable2: 'CBA'},
            {mock_variable1: 'EFG', mock_variable2: 'DFA'},
        ]

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.consistent(assignment)
                self.assertTrue(result)


    def test_order_domain_values(self):
        self.maxDiff = None
        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2}
        mock_crossword.words = {"AAA", "CCC", "ABA", "BAB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 1)
        mock_crossword.overlaps[mock_variable2, mock_variable1] = (1, 1)
        mock_crossword.neighbors.return_value = {mock_variable1}
        cc = generate.CrosswordCreator(mock_crossword)
        assignment = {}
        
        cases = [
            ({mock_variable1: {"ABA", "BAB"}, mock_variable2: {"AAA", "CCC"}}, ["AAA", "CCC"]),
            ({mock_variable1: {"ABA", "CDC"}, mock_variable2: {"AAA", "BBB"}}, ["BBB", "AAA"]),
            ({mock_variable1: {"ABA", "CBC"}, mock_variable2: {"AAA", "BBB"}}, ["BBB", "AAA"]),
        ]

        for domains, expected in cases:
            with self.subTest(domains=domains, expected=expected):
                cc.domains = domains
                result = cc.order_domain_values(mock_variable2, assignment)
                self.assertListEqual(result, expected)


    def test_select_unassigned_variable_MRV_only(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable)
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable)
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable)
        mock_variable3.length = 3
        mock_variable4 = Mock(spec=Variable)
        mock_variable4.length = 3

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3, mock_variable4}
        mock_crossword.words = {"A", "B", "C", "D", "E", "F", "G", "H"}

        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"A"},
            mock_variable2: {"B", "C"},
            mock_variable3: {"D", "E", "F"},
            mock_variable4: {"G", "H"},
        }
        assignment = {}

        result = cc.select_unassigned_variable(assignment)

        self.assertEqual(result, mock_variable1)


    def test_select_unassigned_variable_MRV_plus_degrees(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 3
        mock_variable4 = Mock(spec=Variable, name="var4")
        mock_variable4.length = 3

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3, mock_variable4}
        mock_crossword.words = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}

        def side_effect(value):
            if value == mock_variable1: 
                return {mock_variable2}
            elif value == mock_variable2: 
                return {mock_variable1, mock_variable3}
            elif value == mock_variable3: 
                return {mock_variable1}
            elif value == mock_variable4: 
                return {mock_variable1}

        mock_crossword.neighbors.side_effect = side_effect

        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"A", "B"},
            mock_variable2: {"C", "D"},
            mock_variable3: {"E", "F", "G"},
            mock_variable4: {"H", "I", "J"},
        }
        assignment = {}

        result = cc.select_unassigned_variable(assignment)

        self.assertEqual(result, mock_variable2)

    def test_backtrack_returns_assignment_if_solvable(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 3

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {"ABC", "BCD", "ADG", "AAA", "BBB"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 0)
        mock_crossword.overlaps[mock_variable2, mock_variable1] = (0, 1)
        mock_crossword.overlaps[mock_variable2, mock_variable3] = (2, 1)
        mock_crossword.overlaps[mock_variable3, mock_variable2] = (1, 2)

        def side_effect(value):
            if value == mock_variable1: 
                return {mock_variable2}
            elif value == mock_variable2: 
                return {mock_variable1, mock_variable3}
            elif value == mock_variable3: 
                return {mock_variable2}

        mock_crossword.neighbors.side_effect = side_effect

        cc = generate.CrosswordCreator(mock_crossword)

        assignments = [
            {mock_variable1: 'ABC', mock_variable2: 'BCD', mock_variable3: 'ADG'},
            {mock_variable1: 'ABC', mock_variable2: 'BCD'},
            {mock_variable1: 'ABC'},
            {},
        ]
        
        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = cc.backtrack(assignment)
                self.assertDictEqual(result, assignment)


    def test_backtrack_returns_none_if_unsolvable(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 3
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 3
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 3

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {"ABC", "BCD", "AAA"}
        mock_crossword.overlaps = {}
        mock_crossword.overlaps[mock_variable1, mock_variable2] = (1, 0)
        mock_crossword.overlaps[mock_variable2, mock_variable1] = (0, 1)
        mock_crossword.overlaps[mock_variable2, mock_variable3] = (2, 1)
        mock_crossword.overlaps[mock_variable3, mock_variable2] = (1, 2)

        def side_effect(value):
            if value == mock_variable1: 
                return {mock_variable2}
            elif value == mock_variable2: 
                return {mock_variable1, mock_variable3}
            elif value == mock_variable3: 
                return {mock_variable2}

        mock_crossword.neighbors.side_effect = side_effect

        cc = generate.CrosswordCreator(mock_crossword)

        assignment = {mock_variable1: 'ABC', mock_variable2: 'BCD'}
        result = cc.backtrack(assignment)
        self.assertIsNone(result)


    def test_get_inferences_from_domains_returns_empty_dict_if_no_inference_in_domains(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 1
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 1
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 1

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
        mock_crossword.overlaps = {}

        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"A", "B"},
            mock_variable2: {"C", "D"},
            mock_variable3: {"E", "F", "G"},
        }
        assignment = {}
        result = cc.get_inferences_from_domains(assignment)
        expected = dict()
        self.assertDictEqual(result, expected)


    def test_get_inferences_from_domains_returns_empty_dict_if_already_in_assignment(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 1
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 1
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 1

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
        mock_crossword.overlaps = {}

        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"A"},
            mock_variable2: {"C", "D"},
            mock_variable3: {"E", "F", "G"},
        }
        assignment = {mock_variable1: "A"}
        result = cc.get_inferences_from_domains(assignment)
        expected = dict()
        self.assertDictEqual(result, expected)

    def test_get_inferences_from_domains(self):
        self.maxDiff = None

        mock_variable1 = Mock(spec=Variable, name="var1")
        mock_variable1.length = 1
        mock_variable2 = Mock(spec=Variable, name="var2")
        mock_variable2.length = 1
        mock_variable3 = Mock(spec=Variable, name="var3")
        mock_variable3.length = 1

        mock_crossword = Mock(spec=Crossword)
        mock_crossword.variables = {mock_variable1, mock_variable2, mock_variable3}
        mock_crossword.words = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
        mock_crossword.overlaps = {}

        cc = generate.CrosswordCreator(mock_crossword)
        cc.domains = {
            mock_variable1: {"A"},
            mock_variable2: {"C", "D"},
            mock_variable3: {"E", "F", "G"},
        }
        assignment = {}
        result = cc.get_inferences_from_domains(assignment)
        expected = {mock_variable1: "A"}
        self.assertDictEqual(result, expected)

# End class



def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(CrosswordCreatorTestCase('test_enforce_node_consistency'))

    suite.addTest(CrosswordCreatorTestCase('test_words_to_remove_unfiltered'))    
    suite.addTest(CrosswordCreatorTestCase('test_words_to_remove_filtered'))    
    suite.addTest(CrosswordCreatorTestCase('test_revise_returns_false_if_no_overlap'))
    suite.addTest(CrosswordCreatorTestCase('test_revise_if_overlap_and_revised'))
    suite.addTest(CrosswordCreatorTestCase('test_revise_if_overlap_and_not_revised'))

    suite.addTest(CrosswordCreatorTestCase('test_ac3'))

    suite.addTest(CrosswordCreatorTestCase('test_assignment_complete_returns_true_if_complete'))
    suite.addTest(CrosswordCreatorTestCase('test_assignment_complete_returns_false_if_incomplete'))

    suite.addTest(CrosswordCreatorTestCase('test_consistent_returns_false_if_not_distinct'))
    suite.addTest(CrosswordCreatorTestCase('test_assignment_complete_returns_false_if_incorrect_length'))
    suite.addTest(CrosswordCreatorTestCase('test_assignment_complete_returns_false_if_conflicts_neighbor'))
    suite.addTest(CrosswordCreatorTestCase('test_assignment_complete'))
    
    suite.addTest(CrosswordCreatorTestCase('test_order_domain_values'))

    suite.addTest(CrosswordCreatorTestCase('test_select_unassigned_variable_MRV_only'))
    suite.addTest(CrosswordCreatorTestCase('test_select_unassigned_variable_MRV_plus_degrees'))

    suite.addTest(CrosswordCreatorTestCase('test_backtrack_returns_assignment_if_solvable'))
    suite.addTest(CrosswordCreatorTestCase('test_backtrack_returns_none_if_unsolvable'))

    suite.addTest(CrosswordCreatorTestCase('test_get_inferences_from_domains_returns_empty_dict_if_no_inference_in_domains'))
    suite.addTest(CrosswordCreatorTestCase('test_get_inferences_from_domains_returns_empty_dict_if_already_in_assignment'))
    suite.addTest(CrosswordCreatorTestCase('test_get_inferences_from_domains'))
        
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())