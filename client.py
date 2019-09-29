import select, socket, sys, Queue, base64

HOST = input("Please input the server address: ")    # The remote host
PORT = 23333          # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
loguser = ''

inputs = [s, sys.stdin]

try:
	while inputs:
		readable, writable, exceptional = select.select(inputs, inputs, inputs)
		for socket in readable:
			if socket is s: # Get from server.
				data = s.recv(65535)
				if data:
					#print data
					words = data.split()
                    			word = words[0] # control symbol.
				        if word == "svr":  # server information.
				        	print "Server message::::"+base64.b64decode(words[1])
				        elif word == "msg":  # return online users.
				            if len(words) == 4: # all message has msg target message sender form.
				            	if words[1] == loguser: #check if client is the correct target
				            		msg = base64.b64decode(words[2])
				            		sender = words[3]
				            		print sender + ": " + msg
				        elif word == "log":  # server log in successful
							loguser = words[1]
				        elif word == "disc":
				            print "Server disconnected with us."
				            sys.exit()
			elif socket is sys.stdin: # Get from console.
				msgToSend = raw_input()
				words = msgToSend.split()
				if len(words) == 0:
					continue #No input
				word = words[0]
				if word == "msg": #send message. follows format "msg <target> <message> <sender>"
					text = msgToSend[len("msg ")+len(words[1])+1:]
					text = base64.b64encode(text)
					msgToSend = "msg "+words[1]+" "+text+" "+loguser
				if word == "log": #check login information.
					print loguser
					continue
				if word == "quit": #client quit
					sys.exit()
				s.sendall(msgToSend)
finally:
	s.sendall("quit")
	s.close()
