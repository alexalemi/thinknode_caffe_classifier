import socket
import os
import json
import struct
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

THINKNODE_HOST = os.getenv("THINKNODE_HOST")
THINKNODE_PORT = int(os.getenv("THINKNODE_PORT"))
THINKNODE_PID  = os.getenv("THINKNODE_PID")
BUFFER_SIZE = 4096
MAGIC_WORD = 174021652
HEADER_SIZE = 8

class ThinkSocket(object):
    """ A context manager wrapping the socket """

    def __init__(self, sock=None):
        logging.debug("initializing ThinkSocket")
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, host=THINKNODE_HOST, port=THINKNODE_PORT):
        logging.debug("Binding to host=%r, port=%r", host, port)
        self.sock.bind((host,port))

    def connect(self, host=THINKNODE_HOST, port=THINKNODE_PORT):
        logging.debug("connection to host=%r, port=%r", host, port)
        self.sock.connect((host, port))

    def listen(self, size):
        logging.debug("Listening...")
        self.sock.listen(size)

    def accept(self):
        logging.debug("Accepting...")
        return self.sock.accept()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        logging.debug("Close socket")
        self.sock.close()

    def send(self, msg):
        msglen = len(msg)
        totalsent = 0
        while totalsent < msglen:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def send_header(self, size):
        """ Send a standard header """
        msg = struct.pack(">II", MAGIC_WORD, size) 
        self.send(msg)

    def send_json(self, data):
        logging.info("Sending JSON message: %r", data)
        msg = json.dumps(data)
        msglen = len(msg)
        self.send_header(msglen)
        self.send(msg)

    def receive(self, msglen):
        logging.debug("Attempting to recieve message")
        bytes_recd = 0
        chunks = []

        while bytes_recd < msglen:
            chunk = self.sock.recv(min(BUFFER_SIZE, msglen - bytes_recd))
            # if we get an empty chunk, we've had an error
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        
        # logging.info("Recieved message: %r", ''.join(chunks))
        return ''.join(chunks)

    def receive_header(self):
        """ Receive the standard header """
        header = self.receive(HEADER_SIZE)
        signature, size = struct.unpack(">II", header)
        if signature != MAGIC_WORD:
            raise RuntimeError("Signature {} != {}".format(signature, MAGIC_WORD))
        return size

    def receive_json(self):
        # Receive the header
        size = self.receive_header()
        msg = self.receive(size)
        return json.loads(msg)

    def register(self):
        logging.debug("Registering..")
        registration_payload = {"type": "registration", "registration": THINKNODE_PID }
        logging.info("Attempting to register with payload: %r", registration_payload)
        self.send_json(registration_payload)

