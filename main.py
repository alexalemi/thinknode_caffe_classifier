# The main entry point for the ThinkNode application.

import tempfile
import base64
import numpy as np

from thinksocket import ThinkSocket
import caffe_classifier

import logging
logging.basicConfig(level=logging.DEBUG)

def process_blobobj_to_file( blobobj ):
    """ Given a blob, dump it to a temporary file, returns the name """
    logging.debug("Attempting to process the blob into a temporary file")
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(base64.b64decode(blobobj["blob"]))
        tmpname = f.name
    return tmpname

def process_input( inputjson ):
    """ given the input json, process it and return the array of scipy arrays """
    logging.debug("Attempting to process the input field into a set of numpy arrays")
    flnames = [ process_blobobj_to_file(blobobj) for blobobj in inputjson ]
    return [ caffe_classifier.caffe.io.load_image(flname) for flname in flnames ]

def classify_images(images):
    """ Given a set of images, classify them and return the top5 probabilities """
    logging.debug("Inside classify_images")
    net = caffe_classifier.create_network()
    prediction = caffe_classifier.classify_images(net, images)
    top = prediction.argsort(1)[:,::-1]

    topcats = caffe_classifier.cats[top[:,:5]]
    topprobs = prediction.take(top[:,:5])

    result = {"classes": topcats.tolist(), "probabilities": topprobs.tolist() }
    return result


def classify_images_probabilities(images):
    """ Given a set of images, classify them and return the raw probabilities """
    logging.debug("Inside classify_images_probabilities")
    net = caffe_classifier.create_network()
    prediction = caffe_classifier.classify_images(net, images)
    result = prediction.tolist()
    return result

def classify_with_model(prototxt_fl, caffemodel_fl, images):
    """ Given a prototxt and caffemodel, classify the images and return the prediction_probs """
    logging.debug("Inside classify_with_model")
    net = caffe_classifier.create_network(prototxt_fl, caffemodel_fl)
    prediction = caffe_classifier.classify_images(net, images)
    result = prediction.tolist()
    return result


def classify_with_model_class_top5(prototxt_fl, caffemodel_fl, classes, images):
    """ Given prototxt and caffemodel and classnames, return the top5 predictions for the images """
    logging.debug("Inside classify_with_model_top5")
    net = caffe_classifier.create_network(prototxt_fl, caffemodel_fl)
    prediction = caffe_classifier.classify_images(net, images)
    top = prediction.argsort(1)[:,::-1]

    cats = np.array(classes)
    topcats = cats[top[:,:5]]
    topprobs = prediction.take(top[:,:5])
    result = {"classes": topcats.tolist(), "probabilities": topprobs.tolist() }
    return result

UID_LOOKUP = {
        "classify_images_v1.0.0" : classify_images,
        "classify_images_probabilities_v1.0.0": classify_images_probabilities,
        "classify_with_model_v1.0.0" : classify_with_model,
        "classify_with_model_class_top5_v1.0.0" : classify_with_model_class_top5
        }

def handle_function_req(function_req):
    """ Handle the function_req appropriately """
    logging.debug("Inside handle_function_req")

    uid = function_req["function"]["uid"]
    logging.info("Running uid: %r", uid)
    args = function_req["function"]["args"]

    if uid == "classify_images_v1.0.0":
        images = process_input(args[0])
        result = classify_images(images)
    elif uid == "classify_images_probabilities_v1.0.0":
        images = process_input(args[0])
        result = classify_images_probabilities(images)
    elif uid == "classify_with_model_v1.0.0":
        prototxt_fl = process_blobobj_to_file(args[0])
        caffemodel_fl = process_blobobj_to_file(args[1])
        images = process_input(args[2])
        result = classify_with_model(prototxt_fl, caffemodel_fl, images)
    elif uid == "classify_with_model_class_top5_v1.0.0":
        prototxt_fl = process_blobobj_to_file(args[0])
        caffemodel_fl = process_blobobj_to_file(args[1])
        cats = args[2]
        images = process_input(args[3])
        result = classify_with_model(prototxt_fl, caffemodel_fl, cats, images)
    else:
        raise NotImplemented("Cannot run uid: %r", uid)

    return result

if __name__ == "__main__":
    logging.debug("Staring main.py...")


    with ThinkSocket() as sock:
        logging.debug("Connecting to socket.")
        sock.connect()
        logging.debug("Sending registration message.")
        sock.register()

        logging.debug("Recieving function_req")
        function_req = sock.receive_json()

        logging.debug("Computing result")
        result = handle_function_req(function_req)
        logging.info("Generated result: %r", result)

        logging.debug("Sending result")
        sock.send_json(result)
        logging.debug("FINISHED")

