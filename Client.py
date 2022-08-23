from os import system
from struct import pack
import sys
import socket
import select

def main():
    """Main function calling the other functions for Client"""
    dateTime, ip, portNumber = getInfo()
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    packet = dt_reqpk(dateTime)
    serverSocket.sendto(bytearray(packet),(ip,portNumber))
    result = select.select([serverSocket],[],[], 1)
    #Checks if there is a responce
    if result == ([],[],[]):
        print("No responce recieved through socket {} in one second\nSystem Exit".format(serverSocket))
        sys.exit()
    #Unpacks infomation
    byte,addy = result[0][0].recvfrom(1024)
    checkBytearray(byte)
    printstatement(byte)
    

def dt_reqpk(reqtype):
    """Creating the DT-Request packet"""
    packet = bytearray(6)
    packet[0] = 0x49
    packet[1] = 0x7E
    packet[2] = 0x00
    packet[3] = 0x01
    packet[4] = 0x00
    #Checking whether the packet should send the date or time
    if reqtype == "date":
        packet[5] = 0x01
    else:
        packet[5] = 0x02
    return packet
    
    
def getInfo():
    """Checking if the inputs from the comand line are correct"""
    date = str(sys.argv[1])
    #Checking whether the first input equals date or time 
    if date != "date" and date != "time":
        print("Invalid first input entered: Need to enter 'date' or 'time'\nSystem Exit")
        sys.exit()           
    userIP = str(sys.argv[2])
    #Checking if it is a valid IP address
    try:
        ip = socket.getaddrinfo(userIP, None, 0, socket.SOCK_STREAM)
    except socket.gaierror:
        print("Invalid second input entered: Invalid IP address\nSystem Exit")
        sys.exit()
    try:
        portNumber = int(sys.argv[3])
        #Checking if the portnumber is between 1024 and 64000
        if 1024 > portNumber > 64000:
            print("Invalid third input eneterd: Port number needs to be between 1024 and 64000\nSystem Exit")
            sys.exit()     
    #Checks if the number isn't an integer       
    except ValueError:
        print("Invalid third input eneterd: Port number needs to be between 1024 and 64000\nSystem Exit")
        sys.exit()   
    
    return date, userIP, portNumber


def packetError():
    """Prints error with packet and exits program if function is called"""
    print("Error with recieved packet: Packet not correct format\nSystem Exit")
    sys.exit()


def checkBytearray(byte):
    """Checks the incoming DT-responce packet(Bytearray) to see if it is valid"""
    #Checks if the packet is the minimuim size 
    if len(byte) < 13:
        packetError()
    hexVersion = byte.hex()
    #Checks is the magic number 
    if hexVersion[0:4]!= "497e":
        packetError()
    #Checks the packet type
    if hexVersion[4:8] != "0002":
        packetError()
    #Checks if it is a valid version
    if hexVersion[8:12] != "0001" and hexVersion[8:12] != "0002" and hexVersion[8:12] != "0003":
        packetError()
    try:
        #Checks the year
        if (byte[6] << 8 | byte[7]) >= 2100:
            packetError()
        #Checks the month
        if 1 > byte[8] or byte[8] > 12:
            packetError()
        #Checks the day
        if 1 > byte[9] or byte[9]> 31:
            packetError()
        #Checks the hour
        if 0 > byte[10] or byte[10] > 23:
            packetError()
        #Checks the minute
        if 0 > byte[11] or byte[11] > 59:
            packetError()
        #Checks the length
        if byte[12] != len(byte):
            packetError()
    #Checks if the inputs in the try are integers 
    except ValueError:
        packetError()


def printstatement(byte):
    """Convert the text into a new bytearray and then decodes it by utf-8"""
    byte_text = bytearray(byte[13:byte[12]])
    decodeText = byte_text.decode('utf-8')
    print((byte[:2]).hex())
    print((byte[2:4]).hex())
    print((byte[4:6]).hex())
    print((byte[6] << 8 | byte[7]))
    print((byte[8]))
    print((byte[9]))
    print((byte[10]))
    print((byte[11]))
    print(byte[12])
    print(decodeText)

    
main()
