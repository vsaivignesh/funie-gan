#!/usr/bin/env python
"""
# > Script for testing FUnIE-GAN 
#    - Paper: https://arxiv.org/pdf/1903.09766.pdf
#
# > Notes and Usage:
#    - set data_dir and model paths
#    - python test_funieGAN.py
#
# Maintainer: Jahid (email: islam034@umn.edu)
# Interactive Robotics and Vision Lab (http://irvlab.cs.umn.edu/)
# Any part of this repo can be used for academic and educational purposes only
"""
import os
import time
import ntpath
import numpy as np
from scipy import misc
from keras.models import model_from_json
## local libs
from utils.data_utils import getPaths, read_and_resize, preprocess, deprocess
from PIL import Image
import imageio
import cv2

## for testing arbitrary local data
data_dir = "/content/funie-gan/data/test/random/"
from utils.data_utils import get_local_test_data
test_paths = getPaths(data_dir)
print ("{0} test images are loaded".format(len(test_paths)))

## create dir for log and (sampled) validation data
samples_dir = "/content/funie-gan/data/Output/"
if not os.path.exists(samples_dir): os.makedirs(samples_dir)

## test funie-gan
#checkpoint_dir  = '/content/funie-gan/saved_models/gen_p/'
#model_name_by_epoch = "model_15320_" 
## test funie-gan-up
checkpoint_dir  = '/content/funie-gan/saved_models/gen_up/'
model_name_by_epoch = "model_35442_" 

model_h5 = checkpoint_dir + model_name_by_epoch + ".h5"  
model_json = checkpoint_dir + model_name_by_epoch + ".json"
# sanity
assert (os.path.exists(model_h5) and os.path.exists(model_json))

# load model
with open(model_json, "r") as json_file:
    loaded_model_json = json_file.read()
funie_gan_generator = model_from_json(loaded_model_json)
# load weights into new model
funie_gan_generator.load_weights(model_h5)
print("\nLoaded data and model")

# testing loop
times = []; s = time.time()
for img_path in test_paths:
    # prepare data
    img_name = ntpath.basename(img_path).split('.')[0]
    im = read_and_resize(img_path, (256, 256))
    im = preprocess(im)
    im = np.expand_dims(im, axis=0) # (1,256,256,3)
    # generate enhanced image
    s = time.time()
    gen = funie_gan_generator.predict(im)
    gen = deprocess(gen) # Rescale to 0-1
    tot = time.time()-s
    times.append(tot)
    # save sample images
    #im = deprocess(im)
    #real = Image.fromarray(im)
    #real.save(samples_dir+img_name+'_real4.png')
    #gener = Image.fromarray(gen)
    #gener.save(samples_dir+img_name+'_gen4.png')
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    imageio.imwrite(samples_dir+img_name+'_real4.png', im[0])
    #Normalizing
    #Could try gen[0]
    #gen = gen.astype(np.uint8)
    gen = cv2.normalize(gen, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    imageio.imwrite(samples_dir+img_name+'_gen.png', gen[0])
    #misc.imsave(samples_dir+img_name+'_real.png', im[0])
    #misc.imsave(samples_dir+img_name+'_gen.png', gen[0])

# some statistics    
num_test = len(test_paths)
if (num_test==0):
    print ("\nFound no images for test")
else:
    print ("\nTotal images: {0}".format(num_test)) 
    # accumulate frame processing times (without bootstrap)
    Ttime, Mtime = np.sum(times[1:]), np.mean(times[1:]) 
    print ("Time taken: {0} sec at {1} fps".format(Ttime, 1./Mtime))
    print("\nSaved generated images in in {0}\n".format(samples_dir))

