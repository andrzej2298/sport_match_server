import tensorflow as tf
import numpy as np

# data constants
RECENT_WORKOUTS_COUNT = 7
BASIC_WORKOUT_FEATURES = 39
RECENT_WORKOUT_FEATURES = 15
RECENT_WORKOUTS_DATA_LENGTH = RECENT_WORKOUTS_COUNT * RECENT_WORKOUT_FEATURES
N = BASIC_WORKOUT_FEATURES + RECENT_WORKOUTS_DATA_LENGTH
TRAIN_DATA_SIZE = 5

# model constants
MIDDLE_LAYER_1_WEIGHT_MULTIPLIER = 2
MIDDLE_LAYER_2_WEIGHT_MULTIPLIER = 3
MIDDLE_LAYER_3_WEIGHT_MULTIPLIER = 5


class RecommendationModel(tf.keras.Model):

    def __init__(self):
        super(RecommendationModel, self).__init__()
        self.input_layer = tf.keras.layers.Dense(N, input_shape=[1, N])
        self.middle_layer1 = tf.keras.layers.Dense(N * MIDDLE_LAYER_1_WEIGHT_MULTIPLIER, activation='relu')
        self.middle_layer2 = tf.keras.layers.Dense(N * MIDDLE_LAYER_2_WEIGHT_MULTIPLIER, activation='relu')
        self.middle_layer3 = tf.keras.layers.Dense(N * MIDDLE_LAYER_3_WEIGHT_MULTIPLIER, activation='relu')
        self.output_layer = tf.keras.layers.Dense(1)

    def call(self, inputs):
        x = self.input_layer(inputs)
        x = self.middle_layer1(x)
        x = self.middle_layer2(x)
        x = self.middle_layer3(x)
        x = self.output_layer(x)
        return x


def get_new_model(weights):
    model = RecommendationModel()
    model.compile(optimizer=tf.keras.optimizers.Adam(0.1),
                  loss='mae',
                  metrics=['mse'])
    model.fit([[1 for _ in range(N)]], [1], epochs=1, batch_size=1)

    if len(weights) > 1:
        converted_weights = [np.array(x) for x in weights]
        model.set_weights(converted_weights)

    return model


def get_ratings(json_weights, data):
    model = get_new_model(json_weights)
    return model.predict(data, batch_size=1)


def train_model(json_weights, data_in, data_out):
    model = get_new_model(json_weights)
    model.fit(data_in, data_out, epochs=1, batch_size=1)
    return [x.tolist() for x in model.get_weights()]
