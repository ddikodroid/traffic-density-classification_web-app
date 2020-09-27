from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
import tensorflow as tf
import numpy as np
import json
from traffic_core.preprocessor import lbp

model_path = './traffic_model/lbp-model.h5'
model = load_model(model_path)

def model_predict(img_path, model=model):
    img = image.load_img(img_path, target_size=(287,304))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds

def decode_predictions(preds, top=2, class_list_path='./traffic_model/class.json'):
  if len(preds.shape) != 2 or preds.shape[1] != 6:
    raise ValueError('`decode_predictions` expects '
                     'a batch of predictions '
                     '(i.e. a 2D array of shape (samples, 6)). '
                     'Found array with shape: ' + str(preds.shape))
  index_list = json.load(open(class_list_path))
  results = []
  for pred in preds:
    top_indices = pred.argsort()[-top:][::-1]
    result = [tuple(index_list[str(i)]) + (pred[i],) for i in top_indices]
    result.sort(key=lambda x: x[2], reverse=True)
    results.append(result)
  return results