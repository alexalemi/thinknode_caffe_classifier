from thinksocket import ThinkSocket
import base64

with ThinkSocket() as sock:
    sock.bind()
    sock.listen(1)
    connection, client_address = sock.accept()
    print "Got connection from client:", client_address

    with ThinkSocket(connection) as conn:
        registration = conn.receive_json()
        print "Got Registration", registration

        with open("test/cat.jpg") as f:
            cat = f.read()
        cat64 = base64.b64encode(cat)

        function_req = {
                "type":"function", 
                "function": {
                    "uid": "classify_images_v1.0.0", 
                    "args": [[{ "type":"base64-encoded-blob",
                            "blob": cat64 }]]
                    }
                }
        conn.send_json(function_req)

        answer = conn.receive_json()

        print "Got answer:", answer
                
