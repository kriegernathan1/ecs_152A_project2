from socket import *

receiver_IP = ""
receiver_port = 3005

sender_IP = ""

# UNCOMMENT LINE BELOW BEFORE SUBMISSION
# sender_port = int(input("Enter the Port number you want your receiver to run: "))
sender_port = 3004

s = socket(AF_INET, SOCK_DGRAM)
s.settimeout(5)

try: 
    f = open("message.txt", "r")
except Exception as e:
    print("Unable to open file due to", e)
    print("exiting...")
    exit()

def stop_and_wait():
    current_payload = ""
    resending_flag = False

    i = 1
    while True:

        #generate the header of packet
        outgoing_message = f'{i}|'

        if not resending_flag:
            current_payload = f.read(1000 - len(str(i)) - 1)

        # insert payload into packet
        outgoing_message += current_payload

        #  stop sending packets if we have reached the end of the file
        if len(current_payload) == 0:
            print("End of File, stopping...")
            break
        

        if resending_flag:
            print("Resending packet #", i)
        

        print("\nCurrent window [", i, "]")
        print("Sequence Number of Packet Sent:", i)
        print("The packet payload is:", outgoing_message)
        # print("The size of the payload is:", len(outgoing_message.encode()))

        s.sendto( outgoing_message.encode() , (receiver_IP, receiver_port))

        try: 
            message, _ = s.recvfrom(2048)
            resending_flag = False 
            sequence_number = int(message.decode().split("|")[0])
            i += 1

            print("Acknowledgment Number Received: ", sequence_number)
        except timeout:
            print("A timeout occured. Resending the packet")
            resending_flag = True
            continue
        


stop_and_wait()