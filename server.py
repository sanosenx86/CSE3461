dir_usr_pwd = dict()
PATH = "userinfo.txt"

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
        print("Conflict username.")
    else:
        dir_usr_pwd[username] = password
        write_user_pwd()
        print("Register succeed.")


def login(username, password):
    if (username not in dir_usr_pwd.keys()) or (dir_usr_pwd[username] != password):
        print("login failed")
    else:
        # TODO: after logged in
        print("logged in")


def main():
    while True:
        pass
        # TODO: finish the main loop


main()
