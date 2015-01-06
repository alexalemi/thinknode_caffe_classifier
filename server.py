from thinksocket import ThinkSocket

with ThinkSocket() as sock:
    sock.bind()
    sock.listen(1)
    connection, client_address = sock.accept()
    print "Got connection from client:", client_address

    with ThinkSocket(connection) as conn:
        registration = conn.receive_json()
        print "Got Registration", registration


        function_req = {"type":"resolved_function", "resolved_function": {"id": "blah", "args": [1.0, 2.0]}}
        conn.send_json(function_req)

        answer = conn.receive_json()

        print "Got answer:", answer
                
