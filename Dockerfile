# This starts from the tleyden5iwx/caffe image
FROM tleyden5iwx/caffe

# Copy my source code
COPY . /src/
WORKDIR /src/

# run the thing
ENTRYPOINT ["python", "/src/main.py"]

