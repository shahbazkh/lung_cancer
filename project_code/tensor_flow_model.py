import tensorflow as tf
import numpy as np
from Inputs import *
import sys
from sklearn.cross_validation import train_test_split

if len(sys.argv) == 4:
    IMAGE_FOLDER = sys.argv[1]
    INPUT_LABELS = sys.argv[2]
    PROCESSED_DIRECTORY = sys.argv[3]
else:
    IMAGE_FOLDER = '/datadrive/data/full_data/stage1'
    INPUT_LABELS = '/datadrive/data/stage1_labels.csv'
    PROCESSED_DIRECTORY = '/datadrive/notebook/Adnan/tutorial_code/processed_images_tutorial'

PROCESSED_IMAGE_BASED_NAME = "processed_patient_scan_{}.npy"

IMG_SIZE_PX = 50
SLICE_COUNT = 20

n_classes = 2
batch_size = 10

x = tf.placeholder('float')
y = tf.placeholder('float')

keep_rate = 0.8

def load_npy(patient_id):
    return np.load(PROCESSED_DIRECTORY+PROCESSED_IMAGE_BASED_NAME.format(patient_id))

def conv3d(x, W):
    return tf.nn.conv3d(x, W, strides=[1,1,1,1,1], padding='SAME')

def maxpool3d(x):
    #                        size of window         movement of window as you slide about
    return tf.nn.max_pool3d(x, ksize=[1,2,2,2,1], strides=[1,2,2,2,1], padding='SAME')


def convolutional_neural_network(x):
    #                # 5 x 5 x 5 patches, 1 channel, 32 features to compute.
    weights = {'W_conv1':tf.Variable(tf.random_normal([3,3,3,1,32])),
               #       5 x 5 x 5 patches, 32 channels, 64 features to compute.
               'W_conv2':tf.Variable(tf.random_normal([3,3,3,32,64])),
               #                                  64 features
               'W_fc':tf.Variable(tf.random_normal([54080,1024])),
               'out':tf.Variable(tf.random_normal([1024, n_classes]))}

    biases = {'b_conv1':tf.Variable(tf.random_normal([32])),
               'b_conv2':tf.Variable(tf.random_normal([64])),
               'b_fc':tf.Variable(tf.random_normal([1024])),
               'out':tf.Variable(tf.random_normal([n_classes]))}

    #                            image X      image Y        image Z
    x = tf.reshape(x, shape=[-1, IMG_SIZE_PX, IMG_SIZE_PX, SLICE_COUNT, 1])

    conv1 = tf.nn.relu(conv3d(x, weights['W_conv1']) + biases['b_conv1'])
    conv1 = maxpool3d(conv1)


    conv2 = tf.nn.relu(conv3d(conv1, weights['W_conv2']) + biases['b_conv2'])
    conv2 = maxpool3d(conv2)

    fc = tf.reshape(conv2,[-1, 54080])
    fc = tf.nn.relu(tf.matmul(fc, weights['W_fc'])+biases['b_fc'])
    fc = tf.nn.dropout(fc, keep_rate)

    output = tf.matmul(fc, weights['out'])+biases['out']

    return output


def train_neural_network(x, x_train, y_train, x_test, y_test):
    prediction = convolutional_neural_network(x)
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-3).minimize(cost)

    hm_epochs = 10
    with tf.Session() as sess:
        sess.run(tf.initialize_all_variables())

        successful_runs = 0
        total_runs = 0

        for epoch in range(hm_epochs):
            epoch_loss = 0
            for idx, data in enumerate(x_train):
                total_runs += 1
                try:
                    X = data[0]
                    Y = y_train[idx][1]
                    _, c = sess.run([optimizer, cost], feed_dict={x: X, y: Y})
                    epoch_loss += c
                    successful_runs += 1
                except Exception as e:
                    # I am passing for the sake of notebook space, but we are getting 1 shaping issue from one
                    # input tensor. Not sure why, will have to look into it. Guessing it's
                    # one of the depths that doesn't come to 20.
                    pass
                    #print(str(e))

            print('Epoch', epoch+1, 'completed out of',hm_epochs,'loss:',epoch_loss)

            correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
            accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

            print('Accuracy:',accuracy.eval({x:x_test, y:y_test}))

        print('Done. Finishing accuracy:')
        print('Accuracy:',accuracy.eval({x:[i[0] for i in validation_data], y:[i[1] for i in validation_data]}))

        print('fitment percent:',successful_runs/total_runs)

def run():
    all_patients, train_patients, test_patients = get_patients(IMAGE_FOLDER, INPUT_LABELS)
    train_data_loaded = [load_npy(pat) for pat in train_patients.ix[:, 0]]
    train_data_loaded_label = train_patients.ix[:, 1]
    train_labels = []
    for label in train_data_loaded_label:
        if label == 1: train_labels.append(np.array([0,1]))
        elif label == 0: train_labels.append(np.array([1,0]))

    x_train, x_test, y_train, y_test = train_test_split(train_data_loaded, train_labels, test_size=.2, random_state=2017)

    train_neural_network(x, x_train, y_train, x_test, y_test)

if __name__ == '__main__':
    """
    run 3d cnn using tensorflow
    """
    run()
