#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# test2

import base64
import cStringIO
import sys
import tempfile
import os
import werkzeug
from datetime import datetime

MODEL_BASE = '/opt/models/research'
sys.path.append(MODEL_BASE)
sys.path.append(MODEL_BASE + '/object_detection')
sys.path.append(MODEL_BASE + '/slim')

from decorator import requires_auth
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_wtf.file import FileField
from flask import make_response
from flask import jsonify
import numpy as np
from PIL import Image
from PIL import ImageDraw
import tensorflow as tf
from utils import label_map_util
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form
from wtforms import ValidationError


app = Flask(__name__)


@app.before_request
@requires_auth
def before_request():
  pass


PATH_TO_CKPT = '/opt/graph_def/frozen_inference_graph.pb'
PATH_TO_LABELS = MODEL_BASE + '/object_detection/data/mscoco_label_map.pbtxt'

content_types = {'jpg': 'image/jpeg',
                 'jpeg': 'image/jpeg',
                 'png': 'image/png'}
extensions = sorted(content_types.keys())


def is_image():
  def _is_image(form, field):
    if not field.data:
      raise ValidationError()
    elif field.data.filename.split('.')[-1].lower() not in extensions:
      raise ValidationError()

  return _is_image


class PhotoForm(Form):
  input_photo = FileField(
      'File extension should be: %s (case-insensitive)' % ', '.join(extensions),
      validators=[is_image()])


class ObjectDetector(object):

  def __init__(self):
    self.detection_graph = self._build_graph()
    self.sess = tf.Session(graph=self.detection_graph)

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    self.category_index = label_map_util.create_category_index(categories)

  def _build_graph(self):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    return detection_graph

  def _load_image_into_numpy_array(self, image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

  def detect(self, image):
    image_np = self._load_image_into_numpy_array(image)
    image_np_expanded = np.expand_dims(image_np, axis=0)

    graph = self.detection_graph
    image_tensor = graph.get_tensor_by_name('image_tensor:0')
    boxes = graph.get_tensor_by_name('detection_boxes:0')
    scores = graph.get_tensor_by_name('detection_scores:0')
    classes = graph.get_tensor_by_name('detection_classes:0')
    num_detections = graph.get_tensor_by_name('num_detections:0')

    (boxes, scores, classes, num_detections) = self.sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    boxes, scores, classes, num_detections = map(
        np.squeeze, [boxes, scores, classes, num_detections])

    return boxes, scores, classes.astype(int), num_detections


def draw_bounding_box_on_image(image, box, color='red', thickness=4):
  draw = ImageDraw.Draw(image)
  im_width, im_height = image.size
  ymin, xmin, ymax, xmax = box
  (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                ymin * im_height, ymax * im_height)
  draw.line([(left, top), (left, bottom), (right, bottom),
             (right, top), (left, top)], width=thickness, fill=color)


def encode_image(image):
  image_buffer = cStringIO.StringIO()
  image.save(image_buffer, format='PNG')
  imgstr = 'data:image/png;base64,{:s}'.format(
      base64.b64encode(image_buffer.getvalue()))
  return imgstr


def detect_objects(image_path):
  image = Image.open(image_path).convert('RGB')
  boxes, scores, classes, num_detections = client.detect(image)
  image.thumbnail((480, 480), Image.ANTIALIAS)

  new_images = {}
  for i in range(num_detections):
    if scores[i] < 0.7: continue
    cls = classes[i]
    if cls not in new_images.keys():
      new_images[cls] = image.copy()
    draw_bounding_box_on_image(new_images[cls], boxes[i],
                               thickness=int(scores[i]*10)-4)

  result = {}
  result['original'] = encode_image(image.copy())

  for cls, new_image in new_images.iteritems():
    category = client.category_index[cls]['name']
    result[category] = encode_image(new_image)

  return result

def detect_objects_no_data(image_path):
  image = Image.open(image_path).convert('RGB')
  boxes, scores, classes, num_detections = client.detect(image)
  image.thumbnail((480, 480), Image.ANTIALIAS)

  new_images = {}
  for i in range(num_detections):
    if scores[i] < 0.7: continue
    cls = classes[i]
    if cls not in new_images.keys():
      new_images[cls] = image.copy()
    draw_bounding_box_on_image(new_images[cls], boxes[i],
                               thickness=int(scores[i]*10)-4)

  result = {}
  #result['original'] = encode_image(image.copy())

  for cls, new_image in new_images.iteritems():
    category = client.category_index[cls]['name']
    result[category] = 'ok'
    #result[category] = encode_image(new_image)

  return result
# ★ポイント1
# limit upload file size : 1MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# ★ポイント2
# ex) set UPLOAD_DIR_PATH=/tmp/uploaded
UPLOAD_DIR = os.getenv("UPLOAD_DIR_PATH")

# rest api : request.files with multipart/form-data
# <form action="/data/upload" method="post" enctype="multipart/form-data">
#   <input type="file" name="uploadFile"/>
#   <input type="submit" value="submit"/>
# </form>
@app.route('/data/upload', methods=['POST'])
def upload_multipart():
    # ★ポイント3
    if 'uploadFile' not in request.files:
        return make_response(jsonify({'result':'uploadFile is required.'}),400)

    file = request.files['uploadFile']
    fileName = file.filename
    if '' == fileName:
        return make_response(jsonify({'result':'filename must not empty.'}),404)

    # ★ポイント4
    saveFileName = datetime.now().strftime("%Y%m%d_%H%M%S_") \
        + werkzeug.utils.secure_filename(fileName)
    file.save(os.path.join(UPLOAD_DIR, saveFileName))
    return make_response(jsonify({'result':'upload OK.'}),200)

# ★ポイント5
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print("werkzeug.exceptions.RequestEntityTooLarge")
    return 'result : file size is overed.'

@app.route('/test')
def test():
  print('test')
  return 'test route'

@app.route('/')
def upload():
  photo_form = PhotoForm(request.form)
  return render_template('upload.html', photo_form=photo_form, result={})


@app.route('/post_api', methods=['POST'])
def postApi():
    with tempfile.NamedTemporaryFile() as temp:
      request.files.get('input_photo').save(temp)
      temp.flush()

# detect_objectのoriginal返さない、数値も入ってる版つくる
      result = detect_objects_no_data(temp.name)

    #return result
    return make_response(jsonify(result),200)

@app.route('/post', methods=['GET', 'POST'])
def post():
  form = PhotoForm(CombinedMultiDict((request.files, request.form)))
  if request.method == 'POST' and form.validate():
    with tempfile.NamedTemporaryFile() as temp:
      #form.input_photo.data.save(temp)
      request.files.get('input_photo').save(temp)
      temp.flush()
      result = detect_objects(temp.name)

    photo_form = PhotoForm(request.form)
    print(result.keys())
    return render_template('upload.html',
                           photo_form=photo_form, result=result)
  else:
    return redirect(url_for('upload'))


client = ObjectDetector()


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=False)
