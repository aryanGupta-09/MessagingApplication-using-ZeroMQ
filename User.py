import zmq
import uuid

def main():
    context = zmq.Context()
    server_socket = context.socket(zmq.REQ)
    server_socket.connect("tcp://localhost:5555") # replace with message-server's ip
    user_id = str(uuid.uuid1())
    groups = {}

    while True:
        choice = input("Enter choice:\n1. Get group list\n2. Join group\n3. Leave group\n4. Send message\n5. Get messages\n6. Exit\n")

        if choice == '1':
            server_socket.send_json({"type": "get_group_list", "user_id": user_id})
            response = server_socket.recv_json()
            print("Available groups:", response['group_list'])
            groups = response['group_list']

        elif choice == '2' or choice == '3' or choice == '4' or choice == '5':
            group_name = input("Enter group name: ")
            if group_name not in groups.keys():
                print("Group doesn't exist")
                continue
            group_ip = groups[group_name].split(':')[0]

            group_socket = context.socket(zmq.REQ)
            group_socket.connect(f"tcp://{group_ip}:5556")

            if choice == '2':
                group_socket.send_json({"type": "join_group", "group_name": group_name, "user_id": user_id})
            elif choice == '3':
                group_socket.send_json({"type": "leave_group", "group_name": group_name, "user_id": user_id})
            elif choice == '4':
                message = input("Enter message: ")
                group_socket.send_json({"type": "send_message", "group_name": group_name, "user_id": user_id, "message": message})
            elif choice == '5':
                timestamp = input("Enter timestamp as HH:MM:SS (optional):")
                group_socket.send_json({"type": "get_messages", "group_name": group_name, "user_id": user_id, "timestamp": timestamp})

            response = group_socket.recv_json()
            print("Server response:", response)

        elif choice=='6':
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
