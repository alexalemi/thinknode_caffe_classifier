from thinksocket import ThinkSocket

with ThinkSocket() as sock:
    sock.connect()

    registration_payload = {"type": "registration", "registration": 1231 }
    sock.send_json(registration_payload)

    function_req = sock.receive_json()
    print "Got function req:", function_req

    result = {"type": "result", "result": {"x":1.0, "y":3.0}}
    sock.send_json(result)



