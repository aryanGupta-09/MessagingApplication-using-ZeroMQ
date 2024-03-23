import zmq
import datetime
import threading

class GroupServer:
    def __init__(self, group_name, server_ip):
        self.group_name = group_name
        self.server_ip = server_ip
        self.users = []
        self.messages = []
        self.lock = threading.Lock()

    def register_with_server(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555") # replace with message-server's ip
        socket.send_json({"type": "register_group", "group_name": self.group_name, "ip_address": self.server_ip, "port": "5556"})
        response = socket.recv_json()
        print("Server response:", response)

    def handle_user_join(self, user_id, group_name):
        if user_id in self.users or group_name != self.group_name:
            print(f"User {user_id} has already joined group {self.group_name} or the group doesn't exist")
            return False
        else:
            self.users.append(user_id)
            print(f"User {user_id} joined group {self.group_name}")
            return True
    
    def handle_user_leave(self, user_id, group_name):
        if user_id not in self.users or group_name != self.group_name:
            print(f"User {user_id} is not in {self.group_name} or the group doesn't exist")
            return False
        else:
            self.users.remove(user_id)
            print(f"User {user_id} left group {self.group_name}")
            return True

    def handle_message(self, user_id, message, group_name):
        if user_id not in self.users or group_name != self.group_name:
            print(f"User {user_id} is not in {self.group_name} or the group doesn't exist")
            return False
        
        def _handle_message_thread(user_id, message):
            with self.lock:
                self.messages.append({'user_id': user_id, 'message': message, 'timestamp': datetime.datetime.now().time().strftime("%H:%M:%S")})
            print(f"Received message from {user_id} in group {self.group_name}")

        message_thread = threading.Thread(target=_handle_message_thread, args=(user_id, message))
        message_thread.start()
        message_thread.join()
        return True
    
    def send_messages_after_timestamp(self, user_id, group_name, timestamp):
        if user_id not in self.users or group_name != self.group_name:
            print(f"User {user_id} is not in {self.group_name} or the group doesn't exist")
            return {"status": "FAIL"}
        
        if timestamp == "":
            return {"messages": self.messages}

        timestamp = datetime.datetime.strptime(timestamp, "%H:%M:%S").time().strftime("%H:%M:%S")

        def _send_messages_after_timestamp_thread():
            with self.lock:
                filtered_messages = [msg for msg in self.messages if msg['timestamp'] >= timestamp]
            return {"messages": filtered_messages}

        send_thread = threading.Thread(target=_send_messages_after_timestamp_thread)
        send_thread.start()
        send_thread.join()
        return _send_messages_after_timestamp_thread()

def main():

    group_name = input("Enter group name: ")
    server_ip = "localhost" # replace with address of current machine
    group_server = GroupServer(group_name, server_ip)
    group_server.register_with_server()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:5556")

    while True:
        message = socket.recv_json()
        print("Received message:", message)

        if message['type'] == 'join_group':
            user_id = message['user_id']
            group_name = message['group_name']
            flag = group_server.handle_user_join(user_id,group_name)
            if flag:
                socket.send_json({"status": "SUCCESS"})
            else:
                socket.send_json({"status": "FAIL"})
                
        elif message['type'] == 'leave_group':
            user_id = message['user_id']
            flag = group_server.handle_user_leave(user_id,group_name)
            if flag:
                socket.send_json({"status": "SUCCESS"})
            else:
                socket.send_json({"status": "FAIL"})
                
        elif message['type'] == 'send_message':
            user_id = message['user_id']
            group_name = message.get('group_name')
            user_message = message['message']
            flag = group_server.handle_message(user_id, user_message, group_name)
            if flag:
                socket.send_json({"status": "SUCCESS"})
            else:
                socket.send_json({"status": "FAIL"})
        
        elif message['type'] == 'get_messages':
            user_id = message['user_id']
            group_name = message.get('group_name')
            timestamp = message.get('timestamp', None)
            messages = group_server.send_messages_after_timestamp(user_id, group_name, timestamp)
            socket.send_json(messages)

if __name__ == "__main__":
    main()
