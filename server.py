import select, socket, sys, Queue

dir_usr_pwd = dict()  # (username, password)
user_login = dict()  # (socketobject, username)
PATH = "userinfo.txt"
HOST = 'localhost'  # Symbolic name meaning all available interfaces
PORT = 23333  # Arbitrary non-privileged port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
inputs = [server, sys.stdin]


def read_user_pwd():
    try:
        with open(PATH, "r+") as file:
            temp = file.read().splitlines()
            print(temp)
            i = 0
            while i < len(temp):
                usr = temp[i]
                pwd = temp[i + 1]
                dir_usr_pwd[usr] = pwd
                i += 2
    except FileNotFoundError:
        file = open(PATH, "w+")
    finally:
        file.close()


def write_user_pwd():
    with open(PATH, "w+") as file:
        for k, v in dir_usr_pwd.items():
            file.write(k + '\n')
            file.write(v + '\n')
    file.close()


def register(username, password):
    if username in dir_usr_pwd.keys():
        return False
    else:
        dir_usr_pwd[username] = password
        write_user_pwd()
        return True


def login(username, password, s):
    if (username in user_login.values()) or (username not in dir_usr_pwd.keys()) or (dir_usr_pwd[username] != password):
        # Does not allow multiple account log in.
        return False
    else:
        user_login[s] = username
        return True


def main():
    read_user_pwd()
    try:
        server.bind((HOST, PORT))
        server.listen(65535)
        while inputs:
            readable, writable, exceptional = select.select(inputs, inputs, inputs)
            for s in readable:
                if s is server:
                    # handle new connect.
                    print
                    "received a connect request from a client "
                    connection, client_address = s.accept()
                    print
                    "connection is {}".format(connection)
                    connection.setblocking(0)
                    connection.send("Please log in or register")
                    inputs.append(connection)
                elif s is sys.stdin:
                    # handle server command.
                    command_input = raw_input()
                    if command_input.strip() == "quit":
                        print
                        "Server quit"
                        for client_socket in inputs[2:]:
                            client_socket.send("disc")  # Client will handle it.
                        sys.exit()
                    else:
                        server.sendall("Server boardcast:" + command_input)
                else:
                    # handle connected.
                    data = s.recv(65535)
                    if data:
                        words = data.split()
                        for i, word in enumerate(words):
                            if s in user_login.keys():  # logged in
                                if word == "msg" and len(
                                        words) == 4:  # make sure "msg target message sender" format exists.
                                    target = words[i + 1]
                                    if target in user_login.keys():
                                        send_socket = user_login[target]
                                        send_socket.send(data)  # client will take care the data.
                                    else:
                                        s.send("target not online")
                                elif word == "online":  # return online users.
                                    s.send(user_login.values())
                                elif word == "quit":  # remove s in all lists.
                                    user_login.pop(s, None)
                                    inputs.remove(s)
                                else:
                                    s.send("server cannot understand what you've send.")
                            else:  # not logged in
                                if word == "login" and len(words) > 2 :
                                    if login(words[1], words[2], s):
                                        s.send("log" + words[1])
                                        s.send("logged in as" + words[1])
                                    else:
                                        s.send("login failed: invalid credential or username already logged in")
                                elif word == "register" and len(words) > 2:
                                    if register(words[1], words[2]):
                                        s.send("successfully registered user" + words[1])
                                    else:
                                        s.send("register failed. Conflict username")
                                else:
                                    s.send("Please log in or register.")
    finally:
        server.close()

main()
