# This starts from the tleyden5iwx/caffe image
FROM tleyden5iwx/caffe

# Copy my source code
COPY . /src/
WORKDIR /src/

# set up fake environment variables
CMD source /src/testbashenv

# run the thing
ENTRYPOINT ["python", "/src/caffe_classifier.py"]

