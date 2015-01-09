from thinksocket import ThinkSocket
import base64
import glob

with ThinkSocket() as sock:
    sock.bind()
    sock.listen(1)
    connection, client_address = sock.accept()
    print "Got connection from client:", client_address

    with ThinkSocket(connection) as conn:
        registration = conn.receive_json()
        print "Got Registration", registration

        
        b64s = []
        for fl in glob.glob("test/imgs/*.jpg"):
            print fl
            with open(fl) as f:
                img = f.read()
            img64 = base64.b64encode(img)
            b64s.append(img64)

        # function_req = {
        #         "type":"function", 
        #         "function": {
        #             "uid": "classify_images_v1.0.0", 
        #             "args": [[ { "type":"base64-encoded-blob",
        #                     "blob": img64 }  for img64 in b64s  ]]
        #             }
        #         }

        function_req = {
                "type":"function", 
                "function": {
                    "uid": "classify_image_v1.0.0", 
                    "args": [ { "type":"base64-encoded-blob",
                            "blob": b64s[0] }  ]
                    }
                }
        conn.send_json(function_req)

        answer = conn.receive_json()

        print "Got answer:", answer
                
