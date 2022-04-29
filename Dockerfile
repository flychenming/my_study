FROM python:3.9
#WORKDIR /flask_test
COPY . .
RUN pip install flask gunicorn gevent flask_paginate cachetools patoolib
EXPOSE 5000
CMD gunicorn -w 2 app:app
