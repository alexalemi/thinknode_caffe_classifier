# Caffe classification driver

import os
import numpy as np

caffe_root = '/opt/caffe/'
import sys
sys.path.insert(0, os.path.join(caffe_root,'python') )

import caffe

DEFAULT_MODEL_FILE = "deploy.prototxt"
DEFAULT_PRETRAINED = "bvlc_googlenet.caffemodel"
DEFAULT_MEAN = "ilsvrc_2012_mean.npy"

# Load the categories
cats = np.load("category_names.npy")

from functools import partial

imagenet_classifier = partial(caffe.Classifier, DEFAULT_MODEL_FILE,
        DEFAULT_PRETRAINED, 
        mean=np.load(DEFAULT_MEAN),
        channel_swap=(2,1,0),
        raw_scale=255,
        image_dims=(256,256))

def create_network(model_file=DEFAULT_MODEL_FILE, pretrained=DEFAULT_PRETRAINED, *args, **kwargs):
    """ Create a network instance and return, any other parameters 
    are passed on through to the caffe.Classifier constructor """
    net = imagenet_classifier(*args,**kwargs)
    net.set_phase_test()
    net.set_mode_cpu()
    return net


def classify_images(net, images):
    """ Use a network to classify images """
    prediction = net.predict(images)  # predict takes any number of images, and formats them for the Caffe net automatically
    return prediction


if __name__ == "__main__":
    net = create_network()
    image = caffe.io.load_image("cat.jpg")

    prediction = classify_images(net, [image])
    top = prediction.argsort(1)[:,::-1]

    print cats[top[:,:5]]
