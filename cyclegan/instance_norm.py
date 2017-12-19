'''
This is a keras implementation of the Instance Normalization layer.
Developed with help from:
 - Batch Norm paper:
     - https://arxiv.org/abs/1502.03167
 - Batchnorm Keras:
     - https://github.com/fchollet/keras/blob/master/keras/layers/normalization.py
 - Instance Norm paper:
     - https://arxiv.org/abs/1607.08022
 - Keras-Theano implementation:
     - https://github.com/jayanthkoushik/neural-style/blob/master/neural_style/fast_neural_style/transformer_net.py

written by shadySource

'''
# from tensorflow.python.keras.engine.topology import Layer
from tensorflow.python.keras.layers import Layer
from tensorflow.python.keras import backend as k
import tensorflow as tf
from tensorflow.python.keras import initializers

class InstanceNormalization(Layer):
    def __init__(self,
                 beta_initializer=None,
                 gamma_initializer=None,
                 epsilon=1e-3,
                 **kwargs):
        super(InstanceNormalization, self).__init__(**kwargs)
        if k.image_data_format() is 'channels_first':
            self.axis = 1
        else: # image channels x.shape[3]
            self.axis = 3
        print()
        self.epsilon = epsilon
        self.beta_initializer = beta_initializer
        self.gamma_initializer = gamma_initializer

    def build(self, input_shape):
        self.gamma = self.add_weight(shape=(input_shape[self.axis],),
                                     initializer=self.gamma_initializer,
                                     trainable=True,
                                     name='gamma')
        self.beta = self.add_weight(shape=(input_shape[self.axis],),
                                    initializer=self.beta_initializer,
                                    trainable=True,
                                    name='beta')
        super(InstanceNormalization, self).build(input_shape)

    def call(self, x):
        # spatial dimensions of input
        if k.image_data_format() is 'channels_first':
            x_w, x_h = (2, 3)
        else:
            x_w, x_h = (1, 2)

        # Very similar to batchnorm, but normalization over individual inputs.

        hw = k.cast(k.shape(x)[x_h]* k.shape(x)[x_w], k.floatx())

        # Instance means
        mu = k.sum(x, axis=x_w)
        mu = k.sum(mu, axis=x_h)
        mu = mu / hw
        mu = k.reshape(mu, (k.shape(mu)[0], k.shape(mu)[1], 1, 1))

        # Instance variences
        sig2 = k.square(x - mu)
        sig2 = k.sum(sig2, axis=x_w)
        sig2 = k.sum(sig2, axis=x_h)
        sig2 = k.reshape(sig2, (k.shape(sig2)[0], k.shape(sig2)[1], 1, 1))

        # Normalize
        y = (x - mu) / k.sqrt(sig2 + self.epsilon)

        # Scale and Shift
        if k.image_data_format() is 'channels_first':
            gamma = k.reshape(self.gamma, (1, k.shape(self.gamma)[0], 1, 1))
            beta = k.reshape(self.beta, (1, k.shape(self.beta)[0], 1, 1))
        else:
            gamma = k.reshape(self.gamma, (1, 1, 1, k.shape(self.gamma)[0]))
            beta = k.reshape(self.beta, (1, 1, 1, k.shape(self.beta)[0]))
        return gamma * y + beta

