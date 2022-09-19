import unittest
import os

import numpy as np

import traffic


class LoadDataTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.data_dir = 'gtsrb-small'
        cls.result = traffic.load_data('gtsrb-small')

    def test_resize_image(self):
        images = [
            np.ones((20,20,3)),
            np.zeros((20,20,3)),
            np.ones((50,50,3)),
            np.zeros((50,50,3)),
            np.ones((30,30,3)),
            np.zeros((30,30,3)),
        ]
        sizes = [
            (32,32),
            (42,42),
            (32,32),
            (42,42),
            (32,32),
            (42,42),
        ]

        for i, _ in enumerate(images):
            with self.subTest(i=i):
                img = images[i]
                img_width, img_height = sizes[i]

                result = traffic.resize_image(img, img_width, img_height)
                expected_shape = (img_width, img_height, 3)
                self.assertTupleEqual(result.shape, expected_shape)


    def test_load_data_returns_tuple_of_two_lists(self):
        self.assertIsInstance(self.result, tuple)
        self.assertEqual(len(self.result), 2)   
        self.assertIsInstance(self.result[0], list) 
        self.assertIsInstance(self.result[1], list) 


    def test_load_data_images_are_numpy_arrays(self):
        for img in self.result[0]:
            with self.subTest(img=img):
                self.assertIsInstance(img, np.ndarray)


    def test_load_data_labels_are_integers(self):
            for label in self.result[1]:
                with self.subTest(label=label):
                    self.assertIsInstance(label, int)

    def test_load_data_returns_right_length(self):
        expected = sum([len(files) for r, d, files in os.walk(self.data_dir)])
        images = len(self.result[0])
        labels = len(self.result[1])
        self.assertEqual(images, expected)
        self.assertEqual(labels, expected)


    def test_load_data_returns_images_of_right_shape(self):
        for img in self.result[0]:
            with self.subTest(img=img):
                result = img.shape
                expected = (traffic.IMG_WIDTH, traffic.IMG_WIDTH, 3)
                self.assertTupleEqual(result, expected)
                
# End class



def suite():
    suite = unittest.TestSuite()
 
    suite.addTest(LoadDataTestCase('test_resize_image'))
    suite.addTest(LoadDataTestCase('test_load_data_returns_tuple_of_two_lists'))
    suite.addTest(LoadDataTestCase('test_load_data_images_are_numpy_arrays'))
    suite.addTest(LoadDataTestCase('test_load_data_labels_are_integers'))
    suite.addTest(LoadDataTestCase('test_load_data_returns_right_length'))
    suite.addTest(LoadDataTestCase('test_load_data_returns_images_of_right_shape'))
        
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())