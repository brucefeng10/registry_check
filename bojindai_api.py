#!/usr/bin/python3
import string
import cv2
# import keras
from keras.models import *
from keras.layers import *
import numpy as np


"""博金贷验证码识别接口"""
characters = string.digits + string.ascii_lowercase


class CNNPredictionBJD(object):
    width, height, n_len, n_class = 98, 32, 4, len(characters)  # image size of this model

    def __init__(self):
        self.model = self.model()

    def model(self):
        input_tensor = Input((self.height, self.width, 3))
        x = input_tensor
        for i, n_cnn in enumerate([2, 2, 2, 2, 2]):
            for j in range(n_cnn):
                x = Conv2D(32*2**min(i, 3), kernel_size=3, padding='same', kernel_initializer='he_uniform')(x)
                x = BatchNormalization()(x)
                x = Activation('relu')(x)
            x = MaxPooling2D(2)(x)

        x = Flatten()(x)
        x = [Dense(self.n_class, activation='softmax', name='c%d' % (i+1))(x) for i in range(self.n_len)]
        model = Model(inputs=input_tensor, outputs=x)

        model.load_weights('./cnn_model/bjd_cnn_98.h5')

        return model

    def make_prediction(self, img_path):
        X = cv2.imread(img_path).reshape(1, self.height, self.width, 3)
        y_pred = self.model.predict(X)
        result = decode(y_pred)

        return result


def decode(y):
    y = np.argmax(np.array(y), axis=2)[:, 0]
    return ''.join([characters[x] for x in y])


if __name__ == '__main__':
    cnnm = CNNPredictionBJD()

    pred = cnnm.make_prediction('./h5sx.png')
    print('prediction: ', pred)


