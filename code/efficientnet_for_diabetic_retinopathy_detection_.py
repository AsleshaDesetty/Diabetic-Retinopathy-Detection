# -*- coding: utf-8 -*-
#EfficientNet  for Diabetic Retinopathy Detection .ipynb

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os
import cv2
import matplotlib.pyplot as plt
import PIL
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model, load_model
from tensorflow.keras import applications
from tensorflow.keras.optimizers import Adam, Adamax
from tensorflow.keras import regularizers
from numpy import asarray
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from tensorflow.keras import backend as K
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint, LearningRateScheduler
import warnings
warnings.filterwarnings("ignore")

os.listdir('../input/retinopathy/DR data')

train = []
label = []

for i in os.listdir('../input/retinopathy/DR data'):
  train_class = os.listdir(os.path.join('../input/retinopathy/DR data', i))
  for j in train_class:
    img_path = os.path.join('../input/retinopathy/DR data', i, j)
    train.append(img_path)
    label.append(i)

print('Number of images available in the dataset: {} \n'.format(len(train)))

train[1:6]

print(label[1:2])
#print(label[3000:3001])
#label

"""# Data visualization"""

fig, axs = plt.subplots(5, 4, figsize = (20, 20))
count = 0
for i in os.listdir('../input/retinopathy/DR data'):
    train_class = os.listdir(os.path.join('../input/retinopathy/DR data', i))
    for j in range(4):
        img = os.path.join('../input/retinopathy/DR data', i, train_class[j])
        img = PIL.Image.open(img)
        axs[count][j].title.set_text(i)
        axs[count][j].imshow(img)
    count += 1

fig.tight_layout()

No_images_per_class = []
Class_name = []
for i in os.listdir('../input/retinopathy/DR data'):
  train_class = os.listdir(os.path.join('../input/retinopathy/DR data', i))
  No_images_per_class.append(len(train_class))
  Class_name.append(i)
  print('Number of images in {} = {} \n'.format(i, len(train_class)))

retina_df = pd.DataFrame({'Image': train,'Labels': label})
retina_df.head()

retina_df.tail()

sns.countplot(label)

fig1, ax1 = plt.subplots()
ax1.pie(No_images_per_class, labels = Class_name, autopct = '%1.1f%%')
plt.show()

df = retina_df.copy()
df.head()

"""# Data Augmentation and Data Generator creation"""

# limiting maximum number of samples in a class to 1600
"""
sample_list=[]
max_size= 1700
groups=df.groupby('Labels')
for label in df['Labels'].unique():
    group=groups.get_group(label)
    sample_count=len(group)
    if sample_count> max_size:
        samples=group.sample(max_size, replace=False, weights=None, random_state=123, axis=0).reset_index(drop=True)
    else:
        samples=group.sample(frac=1.0, replace=False, random_state=123, axis=0).reset_index(drop=True)
    sample_list.append(samples)
df=pd.concat(sample_list, axis=0).reset_index(drop=True)
print (len(df))
print (df['Labels'].value_counts())
"""

# creating new aug directory for augmented images of classes with less than 370 samples
working_dir='/kaggle/working/'
aug_dir=os.path.join(working_dir, 'aug')
if os.path.isdir(aug_dir):
    shutil.rmtree(aug_dir)
os.mkdir(aug_dir)
for label in df['Labels'].unique():
    dir_path=os.path.join(aug_dir,label)
    os.mkdir(dir_path)
print(os.listdir(aug_dir))

# creating augmented images that will store in the newly created aug directory
target=1820 # set the target count for each class in df
gen=ImageDataGenerator(horizontal_flip=True,  rotation_range=20, width_shift_range=.2,
                              height_shift_range=.2, zoom_range=.2)
groups=df.groupby('Labels') # group by class
for label in df['Labels'].unique():  # for every class
    group=groups.get_group(label)  # a dataframe holding only rows with the specified label
    sample_count=len(group)   # determine how many samples there are in this class
    if sample_count< target: # if the class has less than target number of images
        aug_img_count=0
        delta=target-sample_count  # number of augmented images to create
        target_dir=os.path.join(aug_dir, label)  # define where to write the images
        aug_gen=gen.flow_from_dataframe( group,  x_col='Image', y_col=None, target_size=(224,224), class_mode=None,
                                        batch_size=1, shuffle=False, save_to_dir=target_dir, save_prefix='aug-',
                                        save_format='jpg')
        while aug_img_count<delta:
            images=next(aug_gen)
            aug_img_count += len(images)

aug='/kaggle/working/aug'
auglist=os.listdir(aug)
print (auglist)
for i in auglist:
    classpath=os.path.join(aug, i)
    flist=os.listdir(classpath)
    print('class: ', i, '  file count: ', len(flist))

# Displaying some created augmented images from aug directory

fig, axs = plt.subplots(4, 4, figsize = (20, 20))
count = 0
for i in os.listdir('/kaggle/working/aug'):
    train_class = os.listdir(os.path.join('/kaggle/working/aug', i))
    for j in range(4):
        if i!='No_DR':
            img = os.path.join('/kaggle/working/aug', i, train_class[j])
            img = PIL.Image.open(img)
            axs[count][j].title.set_text(i)
            axs[count][j].imshow(img)
    if i!='No_DR':
        count += 1

fig.tight_layout()

# create new aug_df and concatenate with original df
aug_fpaths=[]
aug_labels=[]
classlist=os.listdir(aug_dir)
for i in classlist:
    classpath=os.path.join(aug_dir, i)
    flist=os.listdir(classpath)
    for f in flist:
        fpath=os.path.join(classpath,f)
        aug_fpaths.append(fpath)
        aug_labels.append(i)
Fseries=pd.Series(aug_fpaths, name='Image')
Lseries=pd.Series(aug_labels, name='Labels')
aug_df=pd.concat([Fseries, Lseries], axis=1)
ndf=pd.concat([df,aug_df], axis=0).reset_index(drop=True)
#ndf=df.sample(frac=1.0, replace=False, random_state=123, axis=0).reset_index(drop=True)


print (df['Labels'].value_counts())
print(aug_df['Labels'].value_counts())
print (ndf['Labels'].value_counts())

ndf.head()

ndf = shuffle(ndf)
train, test = train_test_split(ndf, test_size = 0.2)
train.head()

def crop_image_from_gray(img, tol=7):

    if img.ndim == 2:
        mask = img > tol
        return img[np.ix_(mask.any(1),mask.any(0))]
    elif img.ndim == 3:
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask = gray_img > tol
        check_shape = img[:,:,0][np.ix_(mask.any(1),mask.any(0))].shape[0]

        if (check_shape == 0):
            return img
        else:
            img1=img[:,:,0][np.ix_(mask.any(1),mask.any(0))]
            img2=img[:,:,1][np.ix_(mask.any(1),mask.any(0))]
            img3=img[:,:,2][np.ix_(mask.any(1),mask.any(0))]
            img = np.stack([img1,img2,img3],axis=-1)
            return img

def preprocess_fun(image, sigmaX=10):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = crop_image_from_gray(image)
    image = cv2.resize(image, (224, 224))
    image = cv2.addWeighted(image,4, cv2.GaussianBlur(image, (0,0) ,sigmaX), -4, 128)
    return image

train_datagen = ImageDataGenerator(
        rescale = 1./255,
        shear_range = 0.2,
        validation_split = 0.15,
        horizontal_flip=True,
        preprocessing_function = preprocess_fun
)

test_datagen = ImageDataGenerator(rescale = 1./255, preprocessing_function = preprocess_fun)

train_generator = train_datagen.flow_from_dataframe(
    train,
    directory='./',
    x_col="Image",
    y_col="Labels",
    target_size=(224, 224),
    color_mode="rgb",
    class_mode="categorical", #raw
    batch_size=32,
    subset='training')

validation_generator = train_datagen.flow_from_dataframe(
    train,
    directory='./',
    x_col="Image",
    y_col="Labels",
    target_size=(224, 224),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=32,
    subset='validation')

test_generator = test_datagen.flow_from_dataframe(
    test,
    directory='./',
    x_col="Image",
    y_col="Labels",
    target_size=(224, 224),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=32)

"""# Building Model

"""

img_shape = (224,224,3)

model_name='EfficientNetB1'

base_model=tf.keras.applications.EfficientNetB1(include_top=False, weights="imagenet",input_shape=img_shape, pooling='max')

x=base_model.output

x=keras.layers.BatchNormalization(axis=-1, momentum=0.99, epsilon=0.001 )(x)

x = Dense(256, kernel_regularizer = regularizers.l2(l = 0.016),activity_regularizer=regularizers.l1(0.006),
                bias_regularizer=regularizers.l1(0.006) ,activation='relu')(x)

x=Dropout(rate=.50, seed=123)(x)

output=Dense(5, activation='softmax')(x)

model=Model(inputs=base_model.input, outputs=output)

#model.summary()

"""# Compilation and Training of Model"""

#model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics= ['accuracy'])
model.compile(Adamax(learning_rate=.001), loss='categorical_crossentropy', metrics=['accuracy'])
#model.compile(loss='categorical_crossentropy', optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),metrics=['accuracy'])

earlystopping = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=25)

checkpointer = ModelCheckpoint(filepath="EfficientNet_weights.hdf5", verbose=1, save_best_only=True)

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=0.0001)

history = model.fit(train_generator, steps_per_epoch = train_generator.n // 32, epochs = 100, validation_data= validation_generator, validation_steps= validation_generator.n // 32, callbacks=[checkpointer , reduce_lr, earlystopping], )
#class_weight=class_weight

history.history['val_loss']

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train_loss','val_loss'])
plt.show()

"""# Assessment of Trained model"""

model.load_weights("EfficientNet_weights.hdf5")

#sns.set(font_scale=3.0)

# Evaluate the performance of the model
evaluate = model.evaluate(test_generator, steps = test_generator.n // 32, verbose =1)

print('Accuracy Test : {}'.format(evaluate[1]))

labels = {0: 'Mild', 1: 'Moderate', 2: 'No_DR', 3:'Proliferate_DR', 4: 'Severe'}

prediction = []
original = []
image = []
count = 0

for item in range(len(test)):
    img = PIL.Image.open(test['Image'].tolist()[item])
    img =  preprocess_fun(asarray(img))
    image.append(img)
    img = np.asarray(img, dtype= np.float32)
    img = img / 255
    img = img.reshape(-1,224,224,3)
    predict = model.predict(img)
    predict = np.argmax(predict)
    prediction.append(labels[predict])
    original.append(test['Labels'].tolist()[item])

score = accuracy_score(original, prediction)
print("Test Accuracy : {}".format(score))

import random
fig=plt.figure(figsize = (100,100))
for i in range(20):
    j = random.randint(0,len(image))
    fig.add_subplot(20, 1, i+1)
    plt.xlabel("Prediction: " + str(prediction[j]) +"   Original: " + str(original[j]))
    plt.imshow(image[j])
fig.tight_layout()
plt.show()

print(classification_report(np.asarray(original), np.asarray(prediction)))

# Confusion matrix
plt.figure(figsize = (20,20))
cm = confusion_matrix(original,prediction, normalize='true')
ax = plt.subplot()
sns.heatmap(cm, annot = True, ax = ax, xticklabels=['Mild','Moderate','No_DR','Proliferate_DR','Severe'], yticklabels=['Mild','Moderate','No_DR','Proliferate_DR','Severe'])
# xticklabels=['Mild','Moderate','No_DR','Proliferate_DR','Severe'], yticklabels=['Mild','Moderate','No_DR','Proliferate_DR','Severe']
ax.set_xlabel('Predicted')
ax.set_ylabel('Original')
ax.set_title('Confusion_matrix')



