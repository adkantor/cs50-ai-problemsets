# Traffic
### Project 5 for CS50's Introduction to Artificial Intelligence with Python
<br>

See presentation on implementation here: [CS50AI - Traffic](https://youtu.be/tBNQhtWdWIs)
<br><br>

## Task
Write an AI to identify which traffic sign appears in a photograph.
```
$ python traffic.py gtsrb
Epoch 1/10
500/500 [==============================] - 5s 9ms/step - loss: 3.7139 - accuracy: 0.1545
Epoch 2/10
500/500 [==============================] - 6s 11ms/step - loss: 2.0086 - accuracy: 0.4082
Epoch 3/10
500/500 [==============================] - 6s 12ms/step - loss: 1.3055 - accuracy: 0.5917
Epoch 4/10
500/500 [==============================] - 5s 11ms/step - loss: 0.9181 - accuracy: 0.7171
Epoch 5/10
500/500 [==============================] - 7s 13ms/step - loss: 0.6560 - accuracy: 0.7974
Epoch 6/10
500/500 [==============================] - 9s 18ms/step - loss: 0.5078 - accuracy: 0.8470
Epoch 7/10
500/500 [==============================] - 9s 18ms/step - loss: 0.4216 - accuracy: 0.8754
Epoch 8/10
500/500 [==============================] - 10s 20ms/step - loss: 0.3526 - accuracy: 0.8946
Epoch 9/10
500/500 [==============================] - 10s 21ms/step - loss: 0.3016 - accuracy: 0.9086
Epoch 10/10
500/500 [==============================] - 10s 20ms/step - loss: 0.2497 - accuracy: 0.9256
333/333 - 5s - loss: 0.1616 - accuracy: 0.9535
```

## Background
In this project, you?ll use TensorFlow to build a neural network to classify road signs based on an image of those signs. To do so, you?ll need a labeled dataset: a collection of images that have already been categorized by the road sign represented in them.

Several such data sets exist, but for this project, we?ll use the German Traffic Sign Recognition Benchmark (GTSRB) dataset, which contains thousands of images of 43 different kinds of road signs.

## Specification
Complete the implementation of ```load_data``` and ```get_model``` in ```traffic.py```.
<br><br>

- The ```load_data``` function should accept as an argument ```data_dir```, representing the path to a directory where the data is stored, and return image arrays and labels for each image in the data set.
    - You may assume that ```data_dir``` will contain one directory named after each category, numbered ```0``` through ```NUM_CATEGORIES - 1```. Inside each category directory will be some number of image files.
    - Use the OpenCV-Python module (```cv2```) to read each image as a ```numpy.ndarray``` (a numpy multidimensional array). To pass these images into a neural network, the images will need to be the same size, so be sure to resize each image to have width ```IMG_WIDTH``` and height ```IMG_HEIGHT```.
    - The function should return a tuple ```(images, labels)```. images should be a list of all of the images in the data set, where each image is represented as a ```numpy.ndarray``` of the appropriate size. labels should be a list of integers, representing the category number for each of the corresponding images in the images list.
    - Your function should be platform-independent: that is to say, it should work regardless of operating system. Note that on macOS, the ```/``` character is used to separate path components, while the ```\``` character is used on Windows. Use ```os.sep``` and ```os.path.join``` as needed instead of using your platform?s specific separator character.

- The ```get_model``` function should return a compiled neural network model.
    - You may assume that the input to the neural network will be of the shape ```(IMG_WIDTH, IMG_HEIGHT, 3)``` (that is, an array representing an image of width ```IMG_WIDTH```, height ```IMG_HEIGHT```, and ```3``` values for each pixel for red, green, and blue).
    - The output layer of the neural network should have ```NUM_CATEGORIES``` units, one for each of the traffic sign categories.
    - The number of layers and the types of layers you include in between are up to you. You may wish to experiment with:
        - different numbers of convolutional and pooling layers
        - different numbers and sizes of filters for convolutional layers
        - different pool sizes for pooling layers
        - different numbers and sizes of hidden layers
        - dropout

- Document (in at least a paragraph or two) your experimentation process. What did you try? What worked well? What didn?t work well? What did you notice?

Ultimately, much of this project is about exploring documentation and investigating different options in cv2 and tensorflow and seeing what results you get when you try them!

You should not modify anything else in ```traffic.py``` other than the functions the specification calls for you to implement, though you may write additional functions and/or import other Python standard library modules. You may also import ```numpy``` or ```pandas```, if familiar with them, but you should not use any other third-party Python modules. You may modify the global variables defined at the top of the file to test your program with other values.
<br><br>

---

# The experimentation process

## Step 1: build a naive benchmark model

As a naive benchmark model I've chosen Logistic Regression used as multiclass estimator, with input data reshaped to 1D and one-hot encoded labels.

Validation of the model performance was made using *10-fold Cross-Validation*.

### Results
- **Small dataset**: Accuracy: 0.999 with Standard Deviation: 0.004
- **Large dataset**: Accuracy: 0.926 with Standard Deviation: 0.005

>**Note**: for details see *traffic_notebook_benchmark.ipynb* or *traffic_notebook_benchmark.html*

---

## Step 2: build simple Sequential model (without convolution) as benchmark

To explore effect of different layer sizes and number of layers I built some models without convolution, using the **Small dataset**. Models were trained for 20 epochs.

Evaluation was made on a 20% hold-out test set.

### Results

- **1 hidden layer of 8 units**

    loss=0.0072, accuracy=100.000%

    Both train and test accuracy plateaued after epoch 12 while loss showed minimal decrease even in the last epochs.

- **1 hidden layer of 128 units**

    loss=0.0041, accuracy=100.000%

    Both train and test accuracy plateaued after epoch 12 while loss showed minimal decrease even in the last epochs.

- **3 hidden layers of 128 units**

    loss=0.0005, accuracy=100.000%

    Train accuracy plateaued after epoch 4 at 100% while test accuracy plateaued after epoch 2 at 99.26%. Loss remained unchanged after epoch 10.

I've chosen to proceed with **1 hidden layers of 128 units**.

## Step 3: add convolutional layers (still on Small dataset)

I added a single convolutional layer with 32 filters using 3x3 kernel.

Decreased number of epochs to 10.

### Results

    loss=0.0009, accuracy=100.000%

    Both train and test accuracy plateaued after epoch 4. Loss remained unchanged after epoch 6.

---

## Step 4: Try model of step 3 on Large dataset.

### Results

    loss=0.1931, accuracy=95.852%

    Both train and test accuracy plateaued after epoch 4. Loss remained unchanged after epoch 6.

    Model seems to be slightly ***overfitting*** as validation accuracy plateaued around 95% while train accuracy still showed increasing accuracy during the last epochs.

    The training history also showed significant variance.

---

## Step 5: Explore different configurations

- **Add 25% dropout to the hidden layer, increase number of epochs to 20**

    loss=0.1661, accuracy=96.809%

    Validation accuracy plateaued after epoch 14 at 97% while train accuracy still showed increasing accuracy during the last epochs. Loss remained unchanged after epoch 5 with significant variance.

- **Increase dropout to 50%**

    loss=0.1248, accuracy=96.988%

    Both train/test accuracy and loss showed improvement in the last epochs, so number of epochs needs to be increased.

- **3 hidden layers with 256/128/64 units, increse number of epochs to 40, add early stopping**

    loss=0.1673, accuracy=96.453%

    Seamingly performance has decreased however, history plot shows room for further improvement if number of epochs are increased (performance has not plateaued, early-stopping has not occured).

- **3 convolutional layers with 32 filters using 3x3 kernel, 3 hidden layers 128 units, increse number of epochs to 50**

    loss=0.0576, accuracy=98.649%

    Performance measures show significant improvement after adding more convolutional layers. Early stopping occured after epoch 37.

I decided to use this last model as the Final Model.

>**Note**: for details see *traffic_notebook_models.ipynb* or *traffic_notebook_models.html*