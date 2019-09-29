import select, socket, sys, Queue, base64

dir_usr_pwd = dict()  # (username, password)
user_login = dict()  # (socketobject, username)
PATH = "userinfo.txt"
HOST = input("Please input the server address: ")  # Symbolic name meaning all available interfaces
PORT = 23333     # Arbitrary non-privileged port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##server.setblocking(0)
inputs = [server, sys.stdin]
dead = []


def read_user_pwd():
	try:
		f = open(PATH, "r+")
		temp = f.read().splitlines()
		#print(temp)
		i = 0
		while i < len(temp):
			usr = temp[i]
			pwd = temp[i + 1]
			dir_usr_pwd[usr] = pwd
			i += 2
		f.close()
	except:
		f = open(PATH, "w+")
		f.close()


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
        user_login[username] = s
        return True

def server_msg(msg):
	msg = base64.b64encode(msg)
	return 'svr '+msg #svr means server message

def send_server_message(s, msg):
	try:
		s.send(server_msg(msg))
	except:
		handle_dead_socket(s)

def handle_dead_socket(s):
	inputs.remove(s)
	if s in user_login.keys():
		user_login.pop(s, None)
	s.close()
	
def send_all(msg):
	for s in inputs[2:]:
		try:
			s.send(msg)
		except:
			dead.append(s)
	for s in dead:
		handle_dead_socket(s)
	del dead[:]
	
def main():
    read_user_pwd()
    try:
        server.bind((HOST, PORT))
        server.listen(65535)
        while inputs:
            readable, writable, exceptional = select.select(inputs, inputs, inputs)
            for s in readable:
                if s is server: # handle new connect.
                    print "received a connect request from a client "
                    connection, client_address = s.accept()
                    print "connection is {}".format(connection)
                    # connection.setblocking(0)
                    send_server_message(connection, "Please log in or register")
                    inputs.append(connection)
                elif s is sys.stdin: # handle server command.
                    command_input = raw_input()
                    if command_input.strip() == "quit": # server quit
                        print "Server quit"
			sys.exit()
                    else: # boardcast case
			send_all(server_msg(command_input))
			print "Broadcast sent"
                else:
                    # handle connected.
                    data = s.recv(65535)
                    if data:
                        words = data.split()
                    	word = words[0]
                        if s in user_login.values():  # logged in
			    #print data
                            if word == "msg" and len(words) == 4:  # make sure "msg <target> <message> <sender>" format exists.
                                target = words[1]
                                if target in user_login.keys():
                                    send_socket = user_login[target]
                                    send_socket.send(data)  # client will take care the data.
                                else:
                                    send_server_message(s, "target is not online")
                            elif word == "online":  # return online users.
                                send_server_message(s, str(user_login.keys()))
                            elif word == "quit":  # remove s in all lists.
                                user_login.pop(s, None)
                                inputs.remove(s)
                            else:
                                send_server_message(s, "server cannot understand what you've sent.")
                        else:  # not logged in
                            if word == "login" and len(words) > 2 :
                                if login(words[1], words[2], s):
                                    s.send("log " + words[1]) #keyword "log <username>"
                                    send_server_message(s, "logged in as " + words[1])
                                else:
                                    send_server_message(s, "login failed: invalid credential or username already logged in")
                            elif word == "register" and len(words) > 2:
                                if register(words[1], words[2]):
                                    send_server_message(s, "successfully registered user " + words[1])
                                else:
                                    send_server_message(s, "register failed. Conflict username")
                            else:
                                send_server_message(s, "Please log in or register.")
                                    
		    for s in exceptional:
				handle_dead_socket(s)
    finally:
	send_all("disc") # Client handle the disconnect signal
    	server.close()
    	
main()
