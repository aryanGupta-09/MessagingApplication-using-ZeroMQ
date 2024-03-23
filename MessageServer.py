import zmq

class MessageServer:
    def __init__(self):
        self.groups = {}

    def handle_group_registration(self, group_name, ip_address, port):
        self.groups[group_name] = ip_address+':'+port
        print(f"Registered group {group_name} at {ip_address}:{port}")

    def get_group_list(self, user_id):
        print(f"Group list request from user {user_id}")
        return self.groups

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print("Server is running")

    message_server = MessageServer()

    while True:
        message = socket.recv_json()
        print("Received message:", message)

        if message['type'] == 'register_group':
            group_name = message['group_name']
            ip_address = message['ip_address']
            port = message['port']
            message_server.handle_group_registration(group_name, ip_address, port)
            socket.send_json({"status": "SUCCESS"})

        elif message['type'] == 'get_group_list':
            user_id = message['user_id']
            group_list = message_server.get_group_list(user_id)
            socket.send_json({"group_list": group_list})

if __name__ == "__main__":
    main()
