import unittest
from copy import deepcopy

import heredity as h


class JointProbabilityTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.people = h.load_data('data/family0.csv')

    def test_has_parents(self):
        person_having_no_parents = {
            'name': 'person1',
            'mother': None,
            'father': None,
            'trait': False
        }
        person_having_parents = {
            'name': 'person2',
            'mother': 'person0',
            'father': 'person1',
            'trait': False
        }
        data = [
            (person_having_no_parents, False),
            (person_having_parents, True)
        ]

        for person, expected in data:
            with self.subTest(person=person, expected=expected):
                result = h.has_parents(person)
                self.assertEqual(result, expected)


    def test_get_nr_genes_returns_zero(self):
        expected = 0
        data = [ # (person_name, one_gene, two_genes)
            ('person0', set(), set()),
            ('person0', {'person1'}, set()),
            ('person0', set(), {'person1'}),
            ('person0', {'person1'}, {'person2'}),
            ('person0', {'person1', 'person2'}, {'person3', 'person4'})
        ]
        for person_name, one_gene, two_genes in data:
            with self.subTest(person_name=person_name, one_gene=one_gene, two_genes=two_genes):
                result = h.get_nr_genes(person_name, one_gene, two_genes)
                self.assertEqual(result, expected)


    def test_get_nr_genes_returns_one(self):
        expected = 1
        data = [ # (person_name, one_gene, two_genes)
            ('person1', {'person1'}, set()),
            ('person1', {'person1'}, {'person2'}),
            ('person1', {'person1', 'person2'}, {'person3', 'person4'})
        ]
        for person_name, one_gene, two_genes in data:
            with self.subTest(person_name=person_name, one_gene=one_gene, two_genes=two_genes):
                result = h.get_nr_genes(person_name, one_gene, two_genes)
                self.assertEqual(result, expected)


    def test_get_nr_genes_returns_two(self):
        expected = 2
        data = [ # (person_name, one_gene, two_genes)
            ('person2', set(), {'person2'}),
            ('person2', {'person1'}, {'person2'}),
            ('person2', {'person1', 'person3'}, {'person2', 'person4'})
        ]
        for person_name, one_gene, two_genes in data:
            with self.subTest(person_name=person_name, one_gene=one_gene, two_genes=two_genes):
                result = h.get_nr_genes(person_name, one_gene, two_genes)
                self.assertEqual(result, expected)
    

    def test_get_probs_inherited_nr_genes(self):
        prob_mutation = 0.01
        data = [ # (father_nr_genes, mother_nr_genes, expected)
            (0, 0, {0: 0.9801, 1: 0.0198, 2: 0.0001}),
            (0, 1, {0: 0.4950, 1: 0.5000, 2: 0.0050}),
            (0, 2, {0: 0.0099, 1: 0.9802, 2: 0.0099}),
            (1, 0, {0: 0.4950, 1: 0.5000, 2: 0.0050}),
            (1, 1, {0: 0.2500, 1: 0.5000, 2: 0.2500}),
            (1, 2, {0: 0.0050, 1: 0.5000, 2: 0.4950}),
            (2, 0, {0: 0.0099, 1: 0.9802, 2: 0.0099}),
            (2, 1, {0: 0.0050, 1: 0.5000, 2: 0.4950}),
            (2, 2, {0: 0.0001, 1: 0.0198, 2: 0.9801})
        ]
        for father_nr_genes, mother_nr_genes, expected in data:
            with self.subTest(father_nr_genes=father_nr_genes, mother_nr_genes=mother_nr_genes, expected=expected):
                result = h.get_probs_inherited_nr_genes(father_nr_genes, mother_nr_genes, prob_mutation)
                self.assertDictEqual(result, expected)


    def test_joint_probability(self):
        people = self.people
        one_gene = {"Harry"}
        two_genes = {"James"}
        have_trait = {"James"}
        expected = 0.0026643247488
        result = h.joint_probability(people, one_gene, two_genes, have_trait)
        self.assertEqual(result, expected)

# End class


def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(JointProbabilityTestCase('test_has_parents'))
    suite.addTest(JointProbabilityTestCase('test_get_nr_genes_returns_zero'))
    suite.addTest(JointProbabilityTestCase('test_get_nr_genes_returns_one'))
    suite.addTest(JointProbabilityTestCase('test_get_nr_genes_returns_two'))
    suite.addTest(JointProbabilityTestCase('test_get_probs_inherited_nr_genes'))
    suite.addTest(JointProbabilityTestCase('test_joint_probability'))
        
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())