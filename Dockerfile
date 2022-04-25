FROM python:3.8
#WORKDIR /flask_test
COPY . .
RUN pip install flask gunicorn gevent flask_paginate elasticsearch
EXPOSE 5000
CMD gunicorn -w 2 app:app
