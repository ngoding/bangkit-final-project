# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, request
from flask_cors import CORS
from mtcnn.mtcnn import MTCNN

from keras.models import load_model

# from sklearn.preprocessing import LabelEncoder
# from sklearn.externals import joblib

import numpy as np
from numpy import asarray

from PIL import Image
import json


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)


def clean_name(pins_name):
    return pins_name.replace('pins_', '').replace('_', ' ')


def top_10_prediction(prob, labels):
    label_prob = {}
    result = []
    counter = 0
    for label in labels:
        label_prob[label.replace(' ', '_')] = prob[counter]*100
        counter += 1

    s = sorted(label_prob.items(), key=lambda x: x[1], reverse=True)[:10]
    for k, v in s:
        result.append((clean_name(k), v))
    return result


# load model
# encoder = LabelEncoder()
# encoder.classes_ = np.load('models/face_classes.npy')
# model_svm = joblib.load('models/svm_model.pkl')
model_facenet = load_model('models/facenet_keras.h5')
model_vector_classifier = load_model('models/vector_classifier.h5')
face_classes = json.load(open('models/label_classes.json'))


@app.route('/')
def hello():
    return 'Hello world!'


@app.route('/get-embeddings', methods=['POST'])
def embeddings():
    uploaded_image = request.files['image']

    # extract image
    image = Image.open(uploaded_image)
    image = image.convert('RGB')
    pixels = asarray(image)

    # detect face
    detector = MTCNN()
    results = detector.detect_faces(pixels)
    # bounding box
    x1, y1, width, height = results[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = pixels[y1:y2, x1:x2]
    image = Image.fromarray(face)
    image = image.resize((160, 160))
    face_array = asarray(image)

    # get embedding
    face_pixels = face_array.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean)/std
    samples = np.expand_dims(face_pixels, axis=0)
    embedding = model_facenet.predict(samples)  # get the embedding

    return {
        'embedding': embedding.tolist(),
    }


@app.route('/predict', methods=['POST'])
def predict():
    uploaded_image = request.files['image']

    # extract image
    image = Image.open(uploaded_image)
    image = image.convert('RGB')
    pixels = asarray(image)

    # detect face
    detector = MTCNN()
    results = detector.detect_faces(pixels)
    # bounding box
    x1, y1, width, height = results[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = pixels[y1:y2, x1:x2]
    image = Image.fromarray(face)
    image = image.resize((160, 160))
    face_array = asarray(image)

    # get embedding
    face_pixels = face_array.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean)/std
    samples = np.expand_dims(face_pixels, axis=0)
    embedding = model_facenet.predict(samples)  # get the embedding

    # predict
    # predicted_class = model_svm.predict(embedding)
    # object_classes = encoder.classes_
    # names = object_classes.tolist()
    # predicted_name = clean_name(names[predicted_class[0]])
    # probabilities = model_svm.predict_proba(embedding)[0]
    # predicted_probability = probabilities[predicted_class] * 100
    # top_10 = top_10_prediction(probabilities, encoder.classes_)

    predicted_class = model_vector_classifier.predict_classes(embedding)
    probability = list(model_vector_classifier.predict(embedding)[0])
    predicted_name = face_classes[predicted_class[0]]
    name = f'Predicted {clean_name(predicted_name)} with probabilty '
    formatted_probability = f'{probability[predicted_class[0]]*100:.2f}%'
    result = name + formatted_probability

    return result

    # return {
    #     'name': predicted_name,
    #     'probability': predicted_probability[0],
    #     'top10': top_10
    # }


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
