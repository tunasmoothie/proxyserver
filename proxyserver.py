# Import necessary packages
# All methods from the socket package have been imported as 
# an example
import socket
import sys
#from socket import *


if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py <server_ip> <server_port>"\n<server_ip> : It is the IP Address Of Proxy Server\n<server_port> : It is the Port Of Proxy Server')
    sys.exit(2)

# Optional: take ip address and port as command line arguments or 
# hardcode them in your program, you have various options: localhost,
# custom ip address or ip address of your machine, the latter lets you
# access your server from other devices in the same network
IP_ADDR = sys.argv[1]
PORT = int(sys.argv[2])


# Create a server socket, bind it to a port and start listening
# use AF_INET for address family and SOCK_STREAM for protocol
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((IP_ADDR, PORT))

# Optional but recommended: Print out statements at every significant 
# step of your program, for example: print out the ip address and por
# once you bind the socket
print("Socket binded to {}:{}".format(IP_ADDR, PORT))

# put the socket into listening mode
serverSocket.listen(5)
print("Socket is listening...")

while True:
    print('Ready to serve...')
    (clientSocket, addr) = serverSocket.accept()
    # Establish connection with client
    print('Received a connection from:  ', addr[0], ":", addr[1])
    
    
    # Receive requests (HTTP GET) from the client
    clientRequest = clientSocket.recv(4096).decode()
    print('Received request from client:\n\n' + clientRequest + '\n')
    
    if(len(clientRequest) < 1):
        continue


    # Extract the required information from the client request:
    # eg. webpage and file names
    url = clientRequest.split()[1]
    webServer = url.split('/')[1]
    webServerPort = '80'
    if (webServer.find(':') != -1):
        print(webServer.split(':'))
        temp = webServer.split(':')
        webServer = temp[0]
        webServerPort = temp[1]
    print('webserver: ', webServer, '   port:  ', webServerPort)
    filename = ''
    if (url.find('/', 1) != -1):
        filename = url[url.find('/', 1)+1:]
    #print('filename: ', filename)
    
    fileExist = "false"
    filetouse = url[1:]
    print(filetouse)


    try:
        # Check whether the required files exist in the cache
        # if yes,load the file and send a response back to the client
        f = open(url[1:], "r") 
        outputdata = f.readlines() 
        print(outputdata)
        fileExist = "true"
        # ProxyServer finds a cache hit and generates a response message
        clientSocket.send(b"HTTP/1.1 200 OK\r\n") 
        clientSocket.send(b"Content-Type:text/html\r\n")
        clientSocket.sendall('\n'.join(outputdata).encode())
        
        print('Read file from cache')
 
    # Error handling for file not found in cache
    except IOError:
        # Since the required files were not found in cache,
        # create a socket on the proxy server to send the request
        # to the actual webserver
        
        webServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        try:
            # Connect your client socket to the webserver at port 80
            webServerSocket.connect((webServer, int(webServerPort)))
            webServerSocket.settimeout(1)
            print("Connected to", webServer)
            
            try:
                # send request to the webserver
                req = "GET /" + filename + " HTTP/1.1\r\nHost:" + webServer + "\r\n\r\n"
                print('Requesting webserver with:\n' + req)
                #webServerSocket.makefile('r', 0)
                webServerSocket.sendall(req.encode())
                # recieve response from the webserver
                print("Received response from webserver:\n")
                
                data_ls = []
                
                while True:
                    try:
                        buf = webServerSocket.recv(4096)
                        data_ls.append(buf)
                        print(buf)
                        if not buf: 
                            print('END DETECTED')
                            break
                    except:
                        #print('RECV FAILED')
                        break
                data = b''.join(data_ls)
                #print('EXIT RECV LOOP')
                
                # relay response back to the client
                clientSocket.sendall(data)
                print('Response relayed to client')
                

                # Create a new file in the cache for the requested file
                # and save the response for any future requests from the client
                try:
                    print('Saving page ' + filetouse + ' to cache...')
                    sf = open(filetouse, 'w')
                    sf.write(data.decode())
                    sf.close()
                    print('New page saved to cache')
                except:
                    print('Save to cache failed')

            except:
                print("Request to the webserver failed")
                webServerSocket.close()

        except:
            # Unable to connect to the webserver
            print("Unable to connect to the webserver")
            