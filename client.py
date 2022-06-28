
#This is the client side of the file transfer application
#Auther - Isaiah Chiraira 2234099

import sys 
import os
import time
import math
import socket  #needed for TCP/IP connection

class Client:

  #Constructor: Each client will have the following parameters on creation
  def __init__(self, username):
    
    self.username = username
    self.ControlSocket = None  #socket at which the client will be connected to the server
    self.DTPsocket = None
    self.active = False   #state of connection 
    self.MSGList = [] #stores all the messages from the server
    self.isErr = False #used to check if response from the server is an error messege
    self.loggedIn = False # login status
    self.user = None  #used to identify user
    self.mode = None  #data transfer mode
    self.dataConnectionAlive = False
    #TODo ADD other data members

  # Initiates TCP/IP with the server
  def TCPConnection(self, host, portNumber):

    self.host = host #IP address of the server
    self.portNumber = portNumber # port at which the server must listen at

    #Create IPv4 TCP socket for client-server connection
    
    try:

      self.ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      print("socket created successfully")

    except socket.error as err:
      print("socket creation failed with error %s"(err))

    #send connection request to server
    try: 
      self.ControlSocket.connect((self.host, self.portNumber)) 
      print(self.host.recv(8192).decode())
      print("\n Connection successful")

      self.active = 1 #connection now active

    except:

      print("Connection failed")
      time.sleep(3)
      return

  #send commands and arguments to the server
  def send(self, CMD):
    self.ControlSocket.send((CMD + '\r\n').encode())

    #print client command if it is not password
    if CMD[:4] != 'PASS':
      #store message
      self.MSGList.append('Client: ' + CMD)
      print('Client: ', CMD)


  #This function get the server response after the client sends a command
  def getResponse(self):

    response = self.ControlSocket.recv(8192).decode()

    #check if the message is an error message
    if response[0] != '5' and response[0] != '4':
            self.isErr = False
    else:
        self.isErr = True

    #store message
    self.MSGList.append('Server:' + response)

    #print response
    print('Server :', response)
    return response

  def login(self, USER, PASS):

    # The command send to the server is the USER argument and the client username
    CMD = 'USER' + USER
    self.send(CMD) #send username argument to server
    self.getResponse() #get server response

    #check for errors before sending password

    if self.isErr == False:

      #get password and send to server
      CMD = 'PASS' + PASS
      self.send(CMD) #send password argument to server
      self.getResponse() #get server response

    #If there is no error, the login is successful
    if self.isErr == False:
      self.loggedIn = True
      self.user = USER #user will be identified with username
      print("Login Successful")

  #logs user out of the system
  def logout(self):
    
    #Close connection
    CMD = 'QUIT'
    self.send(CMD)
    self.getResponse()
    print('Logout successfull')

  #sets the data transfer mode
  def setMode(self, MODE):
    
    #check if the mode is valid
    if MODE.upper() == 'I' or MODE.upper() == 'A':
      self.mode = MODE.upper()
      CMD = 'TYPE ' + self.mode
      self.send(CMD) #send to server
      self.getResponse() #get server response

    else:

      print("Invalid mode")


  #used to start a passive data connection 
  def passiveConnection(self):

    #argument for a passive connection
    CMD = 'PASV'
    self.send(CMD)
    response = self.getResponse()

    #check for an error
    if self.isErr == False:

      firstIndex = response.find('(')
      lastIndex = response.find(')')

      #get host address and port number
      addr = response[firstIndex+1:lastIndex].split(',')
      self.host = '.'.join(addr[:-2])
      self.portNumber = (int(addr[4]) << 8) + int(addr[5])
      print(self.host, self.portNumber)   


      try:
          # Connect to the server DTP
          self.DTPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.DTPsocket.connect((self.serverDTPname, self.serverDTPport))
          print('Passive Connection Successfull \n')
          
          self.dataConnectionAlive = True

      except:

          print('Failed to connect to ', self.serverDTPname)
          # self.statusMSG = 'Failed to connect to '+ self.serverDTPname
          # self.dataConnectionAlive = False
          time.sleep(3)
          return

  def activeConnection(self):
    # Request for an active connection
    try:
      #create socket
      self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      print("socket created successfully")

    except socket.error as err:
      print("socket creation failed with error %s"(err))

    self.c.bind((self.username,0))
    #put server to listening mode
    self.c.listen(1)

    #get IP address and port of client
    IP, portNumber = self.c.getsockname()

    #Read the IP address and port number as per RFC959 standards
    IP = IP.split('.')
    IP = ','.join(IP)

    p1 = math.floor(portNumber/256)
    p2 = portNumber%256

    ### ToDo 
    
    #format the command as per RFC959 standards
    CMD = 'PORT' + IP + ',' + str(p1) + ',' + str(p2)
    self.send(CMD) #send the command
    self.getResponse #get server response

    #initiate the connections
    self.DTPsocket, addr = self.c.accept()
    print('Connected to :' , addr)

    #TODo
    # self.statusMSG  = 'Connected to :' +  str(addr)
    # self.dataConnectionAlive = True

  #downloads file from server, name of file to be downloaded is specified
  def download(self, fileName):

    #format command
    CMD = 'RETR' + fileName
    self.send(CMD) #send to server

    #get server response
    self.getResponse()

    #check for error and continue with download

    if self.isErr == False:

      #check if download directory exists
      downloadDir = 'Downloads'
      if not os.path.exists(downloadDir):
        os.makedirs(downloadDir) #make directory called Downloads

      #check for mode
      if self.mode == 'I':
          outfile = open(downloadDir + '/' + fileName, 'wb')
      else:
          outfile = open(downloadDir + '/' + fileName, 'w') 

      #get data packets
      while 1:
        data = self.DTPsocket.recv(8192)
        if not data:
            break
        outfile.write(data)
      outfile.close()

  def getComm(self):
    return self.MSGList
    
  def clearComm(self):
    self.MSGList.clear()