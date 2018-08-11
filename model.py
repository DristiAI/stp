import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout,BatchNormalization,LSTM
from sklearn.metrics import mean_squared_error as mse 
from keras.optimizers import Adam
import numpy as np
from keras.callbacks import ModelCheckpoint


class my_callbacks(keras.callbacks.Callback):
    def on_train_begin(self,logs={}):
        self.rmse = []
        self.losses = []
    def on_train_end(self,logs={}):
        return
    def on_train_end(self,logs={}):
        return
    def on_epoch_begin(self,epoch,logs={}):
        return
    def on_epoch_end(self,epoch,logs={}):
        self.losses.append(logs.get('loss'))
        y_pred = self.model.predict(self.validation_data[0])
        rmse=np.sqrt(mse(self.validation_data[1],y_pred))
        print('RMSE for  this epoch is {}:'.format(rmse))
        self.rmse.append(rmse)
        return
    def on_batch_begin(self,batch,logs={}):
        return
    def on_batch_end(self,batch,logs={}):
        return
   
    
class init_model():

    def __init__(self):
        self.model = None
        self.save_model=None

    def build_model(self):

        self.model = keras.models.Sequential()
        self.model.add(LSTM(256,activation='tanh',return_sequences=True,input_shape=(1,4,)))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(256,activation='tanh'))
        self.model.add(Dropout(0.25))
        self.model.add(Dense(1))
        self.model.compile(loss='mean_squared_error',optimizer='adam')
    def save_callbacks(self):
        self.save_model = ModelCheckpoint(filepath='model.h5',save_best_only = True)
        

    
