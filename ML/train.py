import sys, random, json
import tkinter as tk
from tkinter import *
import keras
from keras.utils import to_categorical
from keras.models import Model, load_model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, Add, Multiply, Input, BatchNormalization, Layer, Concatenate, LSTM, TimeDistributed
from keras.optimizers import Adam
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import h5py, random
from PIL import Image
from tqdm import tqdm
from glob import glob
sys.path.append("../")
from velibAPI import getLogData, EpochToDate, dataToMlArray, sortSelect, stationsInfos

x_train = []
x_test = []
meta_train = []
meta_test = []
y_train = []
y_test = []

def processLogs(process=0, save=0, offset=1, batchSize=1):
    global x_train, meta_train, y_train
    folderPath = "off"+str(offset)+"_batch"+str(batchSize)
    if process == 1:
        logs = glob("../data/logs/*")
        for logId in tqdm(range(len(logs)-offset-batchSize)[:40000]):
            rawData, timeStamp = getLogData(logId,"../data/logs/")
            logData, fail = sortSelect(rawData)
            if fail:
                continue
            logData = dataToMlArray(logData)
            logData = [logData[station] for station in logData]
            x_train.append(logData)
            date = EpochToDate(timeStamp,weekday=1,day=0).split(":")
            weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
            meta_train.append([weekday,hour,minutes])

            logData,_ = sortSelect(getLogData(logId+offset,"../data/logs/")[0])
            logData = dataToMlArray(logData)
            #logData = [logData[station] for station in logData]
            targetStationData = rawData[27033125]
            y_train.append(round(targetStationData[0]/(targetStationData[0]+targetStationData[2]),2))
        if save == 1:
            with open("preprocessedData/"+folderPath+"/x_train.json", "w") as file:
                json.dump(x_train, file)
            with open("preprocessedData/"+folderPath+"/y_train.json", "w") as file:
                json.dump(y_train, file)
            with open("preprocessedData/"+folderPath+"/meta_train.json", "w") as file:
                json.dump(meta_train, file)
    elif process == 0:
        x_train = json.load(open("preprocessedData/"+folderPath+"/x_train.json", "r"))
        y_train = json.load(open("preprocessedData/"+folderPath+"/y_train.json", "r"))
        meta_train = json.load(open("preprocessedData/"+folderPath+"/meta_train.json", "r"))

processLogs(process=0, save=0, offset=5, batchSize=1)
x_train,meta_train,y_train = shuffle(x_train,meta_train,y_train)
x_train,x_test,meta_train,meta_test,y_train,y_test = train_test_split(x_train,meta_train,y_train, test_size = 0.20)

x_train = np.array(x_train)
x_test  = np.array(x_test)
meta_train = np.array(meta_train)
meta_test  = np.array(meta_test)
y_train = np.array(y_train)
y_test  = np.array(y_test)
print(y_train.shape)
print(x_train.shape)

#x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
#x_test  = np.reshape(x_test , (x_test.shape[0] , 1, x_test.shape[1] ))
#meta_train = np.reshape(meta_train, (meta_train.shape[0], 1, meta_train.shape[1]))
#meta_test  = np.reshape(meta_test , (meta_test.shape[0] , 1, meta_test.shape[1] ))

regularisationParam = 1e-7
kr=keras.regularizers.l1_l2(l1=regularisationParam, l2=regularisationParam)

inp1 = Input(shape=(1436,))
inp2 = Input(shape=(3,))

dataDense = Dense(1436, activation="relu")(inp1)
dataBias  = Dense(1, activation="relu")(inp1)

metaDense = Dense(3, activation="relu")(inp2)
metaBias  = Dense(1, activation="relu")(inp2)

metaMerge = Concatenate()([metaDense,dataBias])
meta      = Dense(4, activation="relu")(metaMerge)

dataMerge = Concatenate()([dataDense,metaBias])
data      = Dense(4, activation="relu")(dataMerge)

merge = Concatenate()([data,meta])

dense = Dense(512, activation="relu")(merge)
dense = Dense(1, activation="sigmoid")(dense)

model = Model(inputs=[inp1,inp2], outputs=dense)
#model = Model(inputs=inp1, outputs=dense)

model.summary()

model.compile(loss="mean_squared_error",
	optimizer=Adam(),
	metrics=["mse","accuracy"])

history = model.fit([x_train,meta_train],y_train,
#history = model.fit(x_train,y_train,
	batch_size = 32,
	epochs = 50,
	#validation_data = (x_test,y_test))
	validation_data = ([x_test,meta_test],y_test))

model.save("netV2.h5")

figure, (ax1, ax2) = plt.subplots(1, 2)
ax1.plot(history.history['loss'], label='train')
ax1.plot(history.history['val_loss'], label='test')
ax1.set_title('Loss')
ax2.plot(history.history['accuracy'], label='train')
ax2.plot(history.history['val_accuracy'], label='test')
ax2.set_title('Accuracy')

plt.legend()
plt.show()
