import sys, random, json
import tkinter as tk
from tkinter import *
import keras
from keras.utils import to_categorical
from keras.models import Model, load_model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, Add, Input, BatchNormalization, Layer, Concatenate
from keras.optimizers import Adam
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import numpy as np
import h5py, random
from PIL import Image
from tqdm import tqdm
from glob import glob
sys.path.append("../")
from velibAPI import getLogData, EpochToDate, dataToMlArray

x_train = []
x_test = []
meta_train = []
meta_test = []
y_train = []
y_test = []

offset = 5

logs = glob("../data/logs/*")
for logId in tqdm(range(len(logs)-offset)):
    rawData, timeStamp = getLogData(logId)
    logData = dataToMlArray(rawData)
    logData = [logData[station] for station in logData]
    x_train.append(logData)

    date = EpochToDate(timeStamp,weekday=1,day=0).split(":")
    weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
    meta_train.append([weekday,hour,minutes])

    logData = dataToMlArray(getLogData(logId+offset)[0])
    logData = [logData[station] for station in logData]
    y_train.append(logData)

x_train,x_test,meta_train,meta_test,y_train,y_test = train_test_split(x_train,meta_train,y_train, test_size = 0.20)

x_train = np.array(x_train)
x_test  = np.array(x_test)
meta_train = np.array(meta_train)
meta_test  = np.array(meta_test)

y_train = np.array(y_train)
y_test  = np.array(y_test)


regularisationParam = 1e-5

inp  = Input(shape=(1446,))
meta = Input(shape=(3,))

dense = Dense(1446, activation="relu", kernel_regularizer=keras.regularizers.l2(l=regularisationParam))(inp)
merge = Concatenate()([dense,meta])
dense = Dense(1446, activation="relu", kernel_regularizer=keras.regularizers.l2(l=regularisationParam))(merge)
dense = Dense(1446, activation="relu", kernel_regularizer=keras.regularizers.l2(l=regularisationParam))(dense)

output = Dense(1446, activation="relu",  kernel_regularizer=keras.regularizers.l2(l=regularisationParam))(dense)

model = Model(inputs=[inp,meta], outputs=output)

model.summary()

model.compile(loss="mean_squared_error",
	optimizer=Adam(),
	metrics=["accuracy"])

model.fit([x_train,meta_train],y_train,
	batch_size = 16,
	epochs = 200,
	validation_data = ([x_test,meta_test],y_test))

model.save("test.h5")
