import sys
import socket
import select
from datetime import datetime


def main():
    """Main function that calls the other functions in Server.py"""
    input1, input2, input3 = getInput()
    English, Maori, German = createSockets(input1, input2, input3)
    #Waiting for a responce    
    result = select.select([English, German, Maori], [], [])
    #Getting the socket that got the repsonce
    used = result[0][0].getsockname()[-1]
    #Finding out the language and return socket
    if used == input1:
        language = 1
        returnSocket = English
    elif used == input2:
        language = 2
        returnSocket = Maori
    else:
        language = 3
        returnSocket = German
    #Getting the pscket as a byte and the address from the data recieved
    byte, addy = result[0][0].recvfrom(6)    
    type = check(byte)
    #Getting the date
    value = str(datetime.now()).split()
    packet = createPacket(type, value, language)
    #Sending the responce
    returnSocket.sendto(packet,addy)
    
            
def getInput():
    """Gets the inputs shown in the command line if there is an error the system will exit"""
    try:
        #Getting inputs 1-3
        input1 = int(sys.argv[1])
        input2 = int(sys.argv[2])
        input3 = int(sys.argv[3])
    #Error if the inputs are integers 
    except ValueError:
        print("All inputs int the command line must be a number.\nSystem Exit")
        sys.exit()
    #Error if there aren't 3 inputs
    except IndexError:
        print("Must input 3 variables into the command line.\nSystem Exit")
        sys.exit()
    #Checking if the numbers are valid: 1024 - 64000
    if 1024 < input1 < 64000 and 1024 < input2 < 64000 and 1024 < input3 < 64000:
        if input1 != input2 and input2 != input3 and input1 != input3:
            return input1, input2, input3
    print("Numbers must be between 1024 and 64000.\nSystem Exit")
    sys.exit()   

    
def createSockets(input1, input2, input3):
    """Creates the 3 sockets and binds the input numbers to them"""
    English = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    English.bind(('', input1))    
    Maori = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    Maori.bind(('', input2))
    German = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    German.bind(('',input3))
    return English, Maori, German


def check(byte):
    """Checking if the recieved packet(Bytearray) is valid"""
    #converting it to hex form 
    hexstring = byte.hex()
    #checing the length
    if len(hexstring) != 12:
        byte_error()
    #checking the magic mumber and checking the packet type
    if hexstring[:4] != "497e" or hexstring[4:8] != "0001":
        byte_error()
    #chekcing if the request type is for date
    if hexstring[8:12] == "0001":
        type = 1
    #checking if the request type is for time
    elif hexstring[8:12] == "0002":
        type = 2
    else:
        byte_error() 
    return type

    
def byte_error():
    """Prints and exits the code if called"""
    print("Recieved packet not in the correct format\nSystem Exit")
    sys.exit()


def createPacket(type, value, language):
    """Creating the DT-Responce packet"""
    packet = bytearray(13)
    packet[0] = 0x49
    packet[1] = 0x7E
    packet[2] = 0x00
    packet[3] = 0x02
    packet[4] = 0x00
    packet[5] = 0x0 + language
    #Putting the date value into a list
    date = value[0].split("-")
    #Putting the time value into a list
    time = value[1].split(":")
    packet[6] = int(date[0]) >> 8
    packet[7] = int(date[0]) & 0x00ff
    packet[8] = int(date[1])
    packet[9] = int(date[2])
    packet[10] = int(time[0])
    packet[11] = int(time[1])
    #checking if the user wants a date responce if not get time responce
    if type == 1:
        text = dateDescription(language, date)
    else:
        text = timeDescription(language, time)
    #adding the text to the end of the header
    packet.extend(text.encode('utf-8'))
    packet[12] = len(packet)
    return packet


def timeDescription(language, time):
    """Creating the time text"""
    #checking the language depending on the recieved port
    if language == 1:
        text = "The current time is {}:{}".format(time[0],time[1])
    elif language == 2:
        text = "Ko te wa o tenei wa {}:{}".format(time[0],time[1])
    else:
        text = "Die Uhrzeit ist {}:{}".format(time[0],time[1])
    return text


def dateDescription(language, date):
    """Creating the date Text"""
    englishMonths = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    maoriMonths = ["Kohitatea ", "Hui-tanguru ", "Poutu-te-rangi", "Paenga-whawha ", "Haratua", "Pipiri", "Hongongoi", "Here-turi-koka", "Mahuru","Whiringa-a-nuku", "Whiringa-a-rangi ", "Hakihea"]
    germanMonths = ["Januar", "Februar", "Marz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    #Checking what language depending on the recieved port
    if language == 1:
        text = "Todays's date is {} {}, {}".format(englishMonths[int(date[1])-1], date[2], date[0])
    elif language == 2:
        text = "Ko te ra o tenei ra ko {} {}, {}".format(maoriMonths[int(date[1])-1], date[2], date[0])
    else:
        text = "Heute ist der {} {}, {}".format(date[2], germanMonths[int(date[1])-1], date[0])
    return text
main()    

