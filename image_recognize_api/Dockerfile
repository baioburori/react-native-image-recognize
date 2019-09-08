# どのイメージを基にするか
#FROM debian
FROM sgoblin/python3.5:latest
# 作成したユーザの情報
#LABEL maintainer="Admin <admin@admin.com>"
# RUN: docker buildするときに実行される
RUN apt-get update
RUN apt-get install -y protobuf-compiler python-pil python-lxml python-pip python-dev git autoconf automake libtool curl make g++ unzip
RUN pip install Flask==0.12.2 WTForms==2.1 Flask_WTF==0.14.2 Werkzeug==0.12.2
RUN pip install --upgrade pip
RUN pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.1.0-cp27-none-linux_x86_64.whl

# protobuf更新
WORKDIR /opt
RUN git clone https://github.com/google/protobuf.git
WORKDIR /opt/protobuf
RUN git checkout v3.6.0
RUN git submodule update --init --recursive
RUN ./autogen.sh
RUN ./configure
RUN make  # 10分〜20分くらいかかります
RUN make check  # 5分〜10分くらいかかります
RUN make install
RUN ldconfig

WORKDIR /opt
RUN git clone https://github.com/tensorflow/models
WORKDIR /opt/models/research
RUN protoc object_detection/protos/*.proto --python_out=.

RUN mkdir -p /opt/graph_def
WORKDIR /tmp

ENV model faster_rcnn_resnet101_coco_11_06_2017
RUN curl -OL http://download.tensorflow.org/models/object_detection/$model.tar.gz
RUN tar -xzf $model.tar.gz $model/frozen_inference_graph.pb
RUN cp -a $model /opt/graph_def/


RUN ln -sf /opt/graph_def/faster_rcnn_resnet101_coco_11_06_2017/frozen_inference_graph.pb /opt/graph_def/frozen_inference_graph.pb

WORKDIR /opt
RUN git clone https://github.com/GoogleCloudPlatform/tensorflow-object-detection-example
RUN cp -a tensorflow-object-detection-example/object_detection_app /opt/
#CMD ["/usr/bin/python","--version"]
ENTRYPOINT ["/opt/object_detection_app/app.py"]
#CMD ["/opt/object_detection_app/app.py"]

RUN mkdir -p /tmp/uploaded
ENV UPLOAD_DIR_PATH /tmp/uploaded
