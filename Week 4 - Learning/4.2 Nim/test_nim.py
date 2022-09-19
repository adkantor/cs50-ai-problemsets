import unittest

import nim


class NimAITestCase(unittest.TestCase):
    
    def setUp(self):
        self.ai = nim.NimAI()

    def test_get_q_value_returns_zero_if_key_not_found(self):
        state = [0, 0, 0, 2]
        action = (3, 2)
        result = self.ai.get_q_value(state, action)
        self.assertEqual(result, 0)

    def test_get_q_value(self):
        self.ai.q[(0, 0, 0, 2), (3, 2)] = -1
        
        state = [0, 0, 0, 2]
        action = (3, 2)
        result = self.ai.get_q_value(state, action)
        self.assertEqual(result, -1)


    def test_best_future_reward_returns_zero_if_no_available_actions(self):
        state = [0, 0, 0, 0]           
        result = self.ai.best_future_reward(state)
        self.assertEqual(result, 0)


    def test_best_future_reward(self):
        self.ai.q[(0, 0, 2, 1), (2, 2)] = 1
        self.ai.q[(0, 0, 2, 1), (2, 1)] = -1
        self.ai.q[(0, 0, 0, 1), (3, 1)] = -1
        states = (
            ([0, 0, 2, 1], 1),
            ([0, 0, 0, 1], -1),
            ([1, 1, 1, 1], 0),
        )
        for state, expected in states:
            with self.subTest(state=state, expected=expected):                
                result = self.ai.best_future_reward(state)
                self.assertEqual(result, expected)


    def test_update_q_value(self):
        self.ai.q[(0, 0, 2, 1), (2, 2)] = 1
        state = [0, 0, 2, 1]
        action = (2, 1)
        old_q = 0
        reward = 0
        future_rewards = -1  
        
        self.assertEqual(len(self.ai.q), 1)
        self.ai.update_q_value(state, action, old_q, reward, future_rewards)
        self.assertEqual(len(self.ai.q), 2)
        self.assertEqual(self.ai.q[(0, 0, 2, 1), (2, 1)], -0.5)


    def test_choose_action_selects_from_all_available_actions_if_epsilon_is_given(self):
        self.ai.q[(0, 0, 2, 1), (2, 2)] = 1
        self.ai.q[(0, 0, 2, 1), (2, 1)] = -1
        self.ai.q[(0, 0, 2, 1), (3, 1)] = -1
        state = [0, 0, 2, 1]
        available_actions = nim.Nim.available_actions(state)
        counts = {
            (2,2): 0,
            (2,1): 0,
            (3,1): 0,
        }
        for _ in range(1000):
            result = self.ai.choose_action(state, epsilon=True)
            counts[result] += 1

        for count in counts.values():
            self.assertGreater(count, 0)

    def test_choose_action_selects_from_best_actions_if_epsilon_is_not_given(self):
        self.ai.q[(0, 0, 2, 1), (2, 2)] = 1
        self.ai.q[(0, 0, 2, 1), (2, 1)] = -1
        self.ai.q[(0, 0, 2, 1), (3, 1)] = 1
        state = [0, 0, 2, 1]

        counts = {
            (2,2): 0,
            (2,1): 0,
            (3,1): 0,
        }
        for _ in range(1000):
            result = self.ai.choose_action(state, epsilon=False)
            counts[result] += 1

        self.assertGreater(counts[(2,2)], 0)
        self.assertGreater(counts[(3,1)], 0)
        self.assertEqual(counts[(2,1)], 0)

# End class



def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(NimAITestCase('test_get_q_value_returns_zero_if_key_not_found'))
    suite.addTest(NimAITestCase('test_get_q_value'))

    suite.addTest(NimAITestCase('test_best_future_reward_returns_zero_if_no_available_actions'))
    suite.addTest(NimAITestCase('test_best_future_reward'))

    suite.addTest(NimAITestCase('test_update_q_value'))

    suite.addTest(NimAITestCase('test_choose_action_selects_from_all_available_actions_if_epsilon_is_given'))
    suite.addTest(NimAITestCase('test_choose_action_selects_from_best_actions_if_epsilon_is_not_given'))
        
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())