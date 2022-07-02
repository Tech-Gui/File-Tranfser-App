#dependencies 
import socket
import os
import time
import threading
import math

'''
Thread class
inheriting from the Thread class found in the threading module
'''
class server_thread(threading.Thread):
    '''
    class constructor
    args : takes in the connection, address, database of the users, the current directory, IP address and port number
    '''
    def __init__(self, connection,address, users, dir,server_IP, server_Port):
        #initializing the base class
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.server_IP = server_IP
        self.server_Port = server_Port
        self.dir = dir
        self.current_dir = dir
        self.rest = False
        self.PASVmode = False
        self.isLogged = False
        self.users = users
        self.isUser = False
        self.isConnected = True
        self.isList = False
        self.mode = 'I'
        self.can_delete = True


    def run(self):
        #The user is connected
        self.isConnected = True
        #response code
        response = "code: 220"
        #send response
        self.sendResponse(response)
        #Wait for connection from clients
        while True:
            command = self.connection.recv(256).decode()
            '''
            check if it is connected or not
            if not, break
            if it is connected, print the command and check if the command is recognized or not 
            '''
            if not command or not isConnected : 
                break
            else :
                print('Recieved: ', command)
                try:
                    function = getattr(self, command[:4].strip().upper())
                    function(command)
                except Exception as err :
                    print(f"Error: {err}")
                    response = "code: 500, syntax error - command unrecognized"
                    self.sendResponse(response)

        # close the connection if thread is not connected     
     
        self.connection.send.close()
    
    # send the reposnse to the server   
    def sendResponse(self, response):
        self.connection.send((response + "\r\n").encode())
    
    # sends a response if the user is not logged in
    def not_logged_in(self):
        response = 'code: 530, please login with the username and password'
        self.sendResponse(response)
    
    # sends a response if the parameters are not correct
    def invalid_parameters(self, command):
        response = f"code: 501, \ {command[:-2]} \ : parameters not understood"
        self.sendResponse(response)

    # reset the state of affairs
    def reset_state(self):
        self.isLogged = False
        self.isUser = False
        self.user = None

    # sends a reposnse of the system tpe
    def system(self, command):
        response = "215 UNIX Type: L8"
        self.sendResponse(response)
    
    # check if the username is valid or not
    def user(self, command):
        # resets the state of the user
        self.reset_state()

        # get the username from the command
        self.user = command[5:-2]

        # get the users
        users = open(self.users, 'r').read()

        # check if the user is there in the users list
        for user in users.split('\n'):
            if self.user == user.split(" ")[0] and len(user.split(" ")[0]) != 0:
                self.isUser = True
                response = "code: 331, username correct, need password"
                self.sendResponse(response)
                break

        if not self.isUser:
            response = "code: 530, Username does not exist"
            self.sendResponse(response)
            self.isUser = False

    # check if the password is correct or not
    def password(self, command):
        # check if the usename is entered
        if self.isUser:
            password = command[5:-2]
            passwords = open(self.users, 'r').read()

            # check if  password matches with the username entered
            for passkey in passwords.split('\n'):
                if password == passkey.split(' ')[1] and self.user == passkey.split(' ')[0]:
                    response = "code: 230, User logged in successfully"
                    self.sendResponse(response)
                    break
            
            if not self.isLogged:
                response = f"code: 530, Invalid password for {self.user}"
                self.sendResponse(response)
        else :
            self.not_logged_in()

    # Logging out
    def logout(self, command):

        #if the user has logged in, log them out
        if self.isLogged:
            self.reset_state()
            response = "code: 221, Successfully logged out"
            self.sendResponse(response)
        else :
            response = "code: 221, Service closing control connection"
            self.sendResponse(response)
            self.isConnected = False
    
    def STRU(self, command):
        stru = command[5]

        if stru == 'F':
            response = "code: 200, F"
        else :
            response = "code: 504, Command obselete"

        self.sendResponse(response)
    
    # streaming mode
    def STRU(self, command):
        _mode = command[5]

        if _mode == 'S':
            response = "code: 200, Mode set to stream"
        else :
            response = "code: 504, Command obselete"
        
        self.sendResponse(response)

    # check if the connection is established or not
    def is_alive(self):
        if self.is_alive():
            response = "code: 200, Connection established"
        else :
            response = "code: 400, There is no connection established"
        
        self.sendResponse(response)

    # choosing modes
    def TYPE(self, command):
        _mode = command[5]

        #check the type of mode 
        if _mode.upper() == 'I':
            self.mode = _mode
            response = "code: 200, Binary mode"
            self.sendResponse(response)
        elif _mode.upper() == 'A':
            self.mode = _mode
            response = "code: 200, ASCII mode" 
            self.sendResponse(response)
        else :
            # unkown mode 
            self.invalid_parameters(command)
    
    # current working directory
    def PWD(self, command):
        #check if the user is looged in
        if self.isLogged:
            #relative path to the root directory
            _dir = '/' + self.current_dir
            current_dir = os.path.relpath(_dir,'/')

            if current_dir == '.':
                current_dir = '/'
            else :
                current_dir = '/' + current_dir
            
            response = f"code: 257, '{current_dir}' is the current directory."
            self.sendResponse(response)

        else :
            self.not_logged_in()

    # current directory
    def CWD(self, command):
        # check if the user has logged in 
        if self.isLogged :
            #get the current directory
            temp_dir = command[4:-2]

            #check if it is the base directory
            if temp_dir == '.' or temp_dir == '/':
                self.current_dir = self.directory
                response = "code: 250, Ok"
                self.sendResponse(response)
            else:
                if temp_dir[0] == '/':
                    temp_dir = temp_dir[1:]

                new_dir = os.path.join(self.current_dir, temp_dir)

                # does the directory exist
                if os.path.exists(new_dir):
                    self.current_dir = new_dir
                    response = "code: 250, Ok"
                    self.sendResponse(response)
                else :
                    response = "code: 550, path does not exist"
                    self.sendResponse(response)
        else :
            self.not_logged_in()

    def PASV(self,command):
        # check if the user is logged in
        if self.is_logged_in():
            self.PASVmode = True

            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.bind(self.server_IP, 0)
            self.serverSocket.listen(1)

            ip, port = self.serverSocket.getsockname()

            ip = ip.split('.')
            ip = ','.join(ip)

            p1 = math.floor(port/256)
            p2 = port % 256
            print(f"open...\nIP: {ip} \nPORT: {port}")

            response = f"code: 227, Passive mode ( {ip}, {p1}, {p2})."
            self.sendResponse(response)

        else :
            self.not_logged_in()
    
    def PORT(self, command):
        # check if the user is looged in
        if self.isLogged:
            # check if passive mode 
            if self.PASVmode:
                self.serverSocket.close()
                self.PASVmode = False
            
            # split the connection settings
            connection_settings = command[5:].split(',')

            # generate the IP address from the connection settings
            self.DTP_address = '.'.join(connection_settings[:4])

            # Generate the port from the connection settings 
            self.DTP_port = (
                (int(connection_settings[4]) << 8) + int(connection_settings[5])
            )

            print(f"Connected to : {self.DTP_address} {self.DTP_port}")

            response = " code: 200, Ok."
            self.sendResponse(response)

            self.DTP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.DTP_socket.connect((self.DTP_address, self.DTP_port))
        else :
            self.not_logged_in()
    
    def start_DTP_socket(self):
        try:
            if self.PASVmode:
                self.DTP_socket, address = self.serverSocket.accept()
                print(f"connect:  {address}")
        except socket.error:
            response = "code: 425, Cannot open data connection"
            self.sendResponse(response)

    def stop_DTP_socket(self):
        self.DTP_socket.close()
        if self.PASVmode:
            self.serverSocket.close()
    
    def send_data(self, data):
        # check mode of sending
        if not self.isList and self.mode == 'I':
            self.DTP_socket.send(data)
        else :
            self.DTP_socket.send((data + '\r\n').encode())

    def List(self, command):
        # check if the user is logged in
        if self.isLogged:
            response = "code: 150, File status okay, about to open connection."
            self.sendResponse(response)
            print(f"list: {self.current_dir}")

            #prepare the socket for data transfer
            self.start_DTP_socket()

            # get each file in the directory
            for file in os.listdir(self.current_dir):
                file_list = self.to_list(os.path.join(self.current_dir, file))
                #send a string
                self.isList = True
                self.send_data(file_list)
                self.isList = False
            
            # Done sending the data
            self.stop_DTP_socket()

            response = "code: 200, Listing completed successfully"
            self.sendResponse(response)
        
        else :
            self.not_logged_in()

    def to_list(self, file):
        # get the status of the file
        status = os.stat(file)
        fullmode = 'rwxrwxrwx'
        mode = ''

        for i in range(9):
            mode += ((status.st_mode >> (8 - i)) & i) and fullmode[i] or '-'

        d = (os.path.isdir(file)) and 'd' or '-'
        file_histor = time.strftime(' %b %d %H:%M', time.gmtime(status.st_mtime))
        return d + mode + '\t1 user' + '\t group \t\t' + str(status.st_size)

    #make directory
    def MKD(self, command):
        #check if the user had logged in       
        if self.isLogged:
            directory_name = os.path.join(self.current_dir, command[4:-2])
            os.mkdir(directory_name)
            response = "code: 257, Directory created."
            self.sendResponse(response)
        else :
            self.not_logged_in()
    
    # delete directory
    def RMD(self, command):
        #check if the user had logged
        if self.isLogged:
            directory_name = os.path.join(self.current_dir, command[4:-2])
            #vcheck if the path exists
            if os.path.exists(directory_name):
                #delete if only delete is enabled
                if self.can_delete:
                    os.rmdir(directory_name)
                    response = "code: 250, Directory deleted."
                    self.sendResponse(response)
                else:
                    response = "code: 450, Delete not allowed."
                    self.sendResponse(response)
            else:
                response = "code: 550, Directory not found."
                self.sendResponse(response)
        else:
            self.not_logged_in()

    # storing files 
    def STOR(self, command):
        # check if the user is looged in
        if self.isLogged:
            #create the file path
            filename = os.path.join(self.current_dir, command[5:-2])
            print(f'Uploading: {filename}')

            #upload modes
            if self.mode == 'I':
                file = open(filename, 'wb')
            else :
                file = open(filename, 'w')
            
            response = "code: 150, Opening data connection."
            self.sendResponse(response)

            #prepare the socket for uploading 
            self.start_DTP_socket()

            #fetch the file contents
            while True:
                data = self.DTP_socket.recv(8192)
                if not data:
                    break
                file.write(data)
            
            # done storing the file 
            self.stop_DTP_socket()
            response = "code: 226, Transfer complete."
            self.sendResponse(response)
            print(f'Upload success.')
            file.close()

        else :
            self.not_logged_in()
    
    def RETR(self, command):
        # check if the user is logged in
        if self.is_logged_in():
            filename = os.path.join(self.current_dir, command[5:-2])

            # for Filezilla
            if filename[0] == '/':
                filename = filename[1:]
            
            # check if file exists
            if os.path.exists(filename):
                print(f"Downloading {filename}.")

                #mode
                if self.mode == 'I':
                    file = open(filename, 'rb')
                else:
                    file = open(filename, 'r')
                
                # open data connection
                response = "code: 150, Opening file data connection."
                self.sendResponse(response)

                data = file.read(8192)
                self.start_DTP_socket()

                # sending the file
                while True:
                    self.send_data(data)
                    data = file.read(8192)
                file.close()
                self.stop_DTP_socket()
                response = "code: 226, Transfer successful."
                self.sendResponse(response)
            else:
                # file does not exist
                response = "code: 550, File does not exist."
                self.sendResponse(response)
        else:
            self.not_logged_in()
        

'''
FTP server class
inheriting from the thread class from the threading module
acts as a lookout class
waits for the connection from the clients
'''
class Server(threading.Thread):
    '''
    class constructor
    takes in the users, home directory, IP address and the port number of the client
    '''
    def __init__(self, users, home_directory, IP, Port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_IP = IP
        self.server_Port = Port
        self.socket.bind(self.server_IP, self.server_Port)
        self.users = users
        self.home_directory = home_directory
        #initializing the base class
        threading.Thread.__init__(self)
    

    '''
    called by the start method in the base class
    an entry point for the threads
    '''
    def run(self):
        self.socket.listen(5)
        while True:
            connection, address = self.socket.accept()
            #create a new thread
            thread = Server_thread(connection, address, self.users, self.home_directory, self.server_IP, self.server_Port)
            thread.deamon = True
            #start the thread
            thread.run()
            
    # stop the server
    def stop(self):
        self.socket.close()


'''
start the application
'''
def Start():
    #port number
    server_Port = 21

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #conenct to the Google DNS
    server.connect("8.8.8.8", 80)
    #get the IP addres of the serve 
    server_IP = server.getsockname()[0]

    #get users 
    users = './users.txt'

    #Home directory
    home_directory = '../'

    # create threars for each client

    Thread = Server(users, home_directory, server_IP, server_Port)
    Thread.daemon = True
    Thread.start()

    # wait for clients to initiate connection
    print(f"File Transfer Application running on {server_IP} : {server_Port}")
    print("Press enter to stop...")
    Thread.stop()

Start()