"""
LSTM_Model.py

This file contains the implementation of the LSTM model for energy production and consumption prediction.
The model takes historical data as input and provides short-term and long-term forecasts.

Usage:
- The LSTM model is used by the Prediction Agent to forecast energy metrics.
- It is trained on historical energy data and can be loaded for inference.

Inputs:
- Historical energy production and consumption data.

Outputs:
- Predicted energy production and consumption values.

Dependencies:
- TensorFlow/Keras for LSTM implementation.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def create_model(input_shape):
    """
    Creates and returns an LSTM model.

    Args:
    input_shape (tuple): Shape of the input data (timesteps, features).

    Returns:
    tf.keras.Model: Compiled LSTM model.
    """
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(2))  # Predicts two outputs: production and consumption
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(model, x_train, y_train, epochs=50, batch_size=32):
    """
    Trains the LSTM model with provided data.

    Args:
    model (tf.keras.Model): LSTM model to be trained.
    x_train (np.array): Training data inputs.
    y_train (np.array): Training data outputs.
    epochs (int): Number of training epochs.
    batch_size (int): Size of the training batches.

    Returns:
    tf.keras.Model: Trained LSTM model.
    """
    model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)
    return model

def load_model(model_path):
    """
    Loads a pre-trained LSTM model from the specified path.

    Args:
    model_path (str): Path to the pre-trained model.

    Returns:
    tf.keras.Model: Loaded LSTM model.
    """
    return tf.keras.models.load_model(model_path)

# Example usage (for training)
# Assuming you have x_train and y_train as numpy arrays of training data
# input_shape = (x_train.shape[1], x_train.shape[2])
# model = create_model(input_shape)
# model = train_model(model, x_train, y_train)
# model.save("lstm_model.h5")
