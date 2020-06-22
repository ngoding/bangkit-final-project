# [START dockerfile]
FROM gcr.io/google_appengine/python

# Install the fortunes binary from the debian repositories.
RUN apt-get update && apt-get install -y fortunes

# Change the -p argument to use Python 2.7 if desired.
RUN virtualenv /env -p python3

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/

# fix mtcnn import error
RUN apt-get update
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN pip install opencv-python

# fix tensorflow 2.2 error
RUN pip install --upgrade pip

RUN pip install -r requirements.txt
ADD . /app/

CMD gunicorn -b :8080 main:app
# [END dockerfile]
