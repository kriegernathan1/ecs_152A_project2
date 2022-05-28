from socket import *
import time 
import math
import matplotlib.pyplot as plt
import signal 


receiver_IP = ""
# receiver_port = int(input("Enter the Port number the receiver is running on: "))
receiver_port = 3005

if receiver_port == 3000:
    print("Sender is hard coded to run on 3000 please pick another port number")

sender_IP = ""

sender_port = 3000

s = socket(AF_INET, SOCK_DGRAM)
s.settimeout(10)

try: 
    f = open("message.txt", "r")
except Exception as e:
    print("Unable to open file due to", e)
    print("exiting...")
    exit()

lowest_sequence_number = 1
all_packets = []
number_of_acks_per_packet = [] 
i = 1
# create all the packets from the message.txt file
all_packets.append("")
while True: 
    header = f'{i}|'
    payload = f.read(1000)

    if len(payload) == 0:
        break

    packet = header + payload
    all_packets.append(packet)

    i += 1

for i in range(len(all_packets)):
    number_of_acks_per_packet.append(0)

def timeout_handler(signum, frame):
    print("Timeout occurred")
    raise timeout


def static_sliding_window():
    global lowest_sequence_number
    global number_of_acks_per_packet

    highest_ack_received = 0

    sent_all_packets = False

    #until we run out of packets to send
    while True:
        send_window()

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        # wait for acks from receiver
        while True:
            try:
                received_seq_number, addr = s.recvfrom(1024)
                
                # convert to int
                received_seq_number = int(received_seq_number.decode())

                print("Acknowledgment Number Received:", received_seq_number)


                #handle the case where acks are skipped due to timeout or retransmission
                if received_seq_number >= highest_ack_received + 1:
                    # print(received_seq_number, "is greater than", highest_ack_received + 1)
                    # number_of_acks_per_packet[received_seq_number] += 1
                    check_for_untracked_acks(highest_ack_received)
                    highest_ack_received = received_seq_number
                else:
                    number_of_acks_per_packet[received_seq_number] += 1
                    
                    
                print(number_of_acks_per_packet)
                if received_seq_number == len(all_packets) - 1:
                    print("Received last packet")
                    return
                

                hasTripleAck , last_ack_received_index = window_has_triple_ack()

                if all_acks_in_window_received():
                    signal.alarm(0)    
                    # set the lowest sequence number to the next packet to send
                    # print("All acks received, moving to next window")
                    print("\n")
                    lowest_sequence_number += 5

                    break
                        
                elif hasTripleAck:
                    signal.alarm(0)
                    print("Triple ack received, fast retransmission of packet #", last_ack_received_index + 1)
                    print("has ", number_of_acks_per_packet[last_ack_received_index], "acks")
                    s.sendto(all_packets[last_ack_received_index + 1].encode(), addr)
                    
  
                
            except timeout:
                signal.alarm(0)
                set_lowest_sequence_number()
                print("No ACK received, resending packets...")
                break

def set_lowest_sequence_number():
    global lowest_sequence_number
    
    while True:
        if lowest_sequence_number > len(all_packets) - 1:
            print("can't set a higher sequence number than the number of packets")
            return
        if number_of_acks_per_packet[lowest_sequence_number] == 1:
            lowest_sequence_number += 1
        else:
            break

def send_window():

    right_most_packet_index = lowest_sequence_number + 5

    # print("sending window: ", lowest_sequence_number, "to", right_most_packet_index)

    if right_most_packet_index > len(all_packets):
        right_most_packet_index = len(all_packets)
    
    if lowest_sequence_number > len(all_packets) - 1:
        return

    print("\nCurrent window:", list(range(lowest_sequence_number, right_most_packet_index)))
    
    for i in range(lowest_sequence_number, right_most_packet_index):

        if number_of_acks_per_packet[i] == 0:
            s.sendto(all_packets[i].encode(), (receiver_IP, receiver_port))
            print("Sequence Number of Packet Sent:", i)
            # print("Packet Sent:", all_packets[i])
        

def all_acks_in_window_received():
    global number_of_acks_per_packet
    right_most_packet_index = lowest_sequence_number + 5

    if right_most_packet_index > len(all_packets):
        right_most_packet_index = len(all_packets) - 1
    
    for i in range(lowest_sequence_number, right_most_packet_index):
        if number_of_acks_per_packet[i] == 0:
            # print(number_of_acks_per_packet[lowest_sequence_number: right_most_packet_index])
            return False
    
    return True

def window_has_triple_ack():
    global number_of_acks_per_packet
    right_most_packet_index = lowest_sequence_number + 5
    
    if right_most_packet_index > len(all_packets):
        right_most_packet_index = len(all_packets) - 1

    
    for i in range(lowest_sequence_number - 1, right_most_packet_index ):
        if number_of_acks_per_packet[i] % 3 == 0 and number_of_acks_per_packet[i] != 0:
            return [True, i]
    
    return [False, None]

def check_for_untracked_acks(highest_ack_received):
    global number_of_acks_per_packet
    right_most_packet_index = highest_ack_received
    
    for i in range(lowest_sequence_number, right_most_packet_index + 1):
        if number_of_acks_per_packet[i] == 0:
            number_of_acks_per_packet[i] = 1


static_sliding_window()
print(number_of_acks_per_packet)