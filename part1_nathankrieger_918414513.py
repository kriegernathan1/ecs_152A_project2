from socket import *
import time 
import math
import matplotlib.pyplot as plt 


receiver_IP = ""
receiver_port = int(input("Enter the Port number the receiver is running on: "))

if receiver_port == 3000:
    print("Sender is hard coded to run on 3000 please pick another port number")

sender_IP = ""

sender_port = 3000

s = socket(AF_INET, SOCK_DGRAM)
s.settimeout(5)

try: 
    f = open("message.txt", "r")
except Exception as e:
    print("Unable to open file due to", e)
    print("exiting...")
    exit()

packet_delays = []
packet_throughputs = []
number_of_packets_lost = 0
total_packets = 0
def stop_and_wait():
    global total_packets
    global number_of_packets_lost
    current_payload = ""
    resending_flag = False

    i = 1
    while True:

        #generate the header of packet
        outgoing_message = f'{i}|'

        if not resending_flag:
            # current_payload = f.read(1000 - len(str(i)) - 1)
            current_payload = f.read(1000)

        # insert payload into packet
        outgoing_message += current_payload

        #  stop sending packets if we have reached the end of the file
        if len(current_payload) == 0:
            # print("End of File, stopping...")
            break
        

        if resending_flag:
            print("Resending packet #", i)
        else:
            print("\nCurrent window [", i, "]")
            print("Sequence Number of Packet Sent:", i)
            # print("The packet payload is:", outgoing_message[0:10])
            # print("The size of the packet is:", len(outgoing_message))
            packet_sending_time = time.time()

        # print("The size of the payload is:", len(outgoing_message.encode()))

        s.sendto( outgoing_message.encode() , (receiver_IP, receiver_port))

        try: 
            message, _ = s.recvfrom(2048)
            resending_flag = False 
            sequence_number = int(message.decode().split("|")[0])
            i += 1

            single_packet_delay = round((time.time() - packet_sending_time) / 1000)
            single_packet_throughput = round((len(outgoing_message) * 8) / (time.time() - packet_sending_time))

            # print("Delay for packet was:", single_packet_delay, "ms")

            packet_delays.append(single_packet_delay)
            packet_throughputs.append(single_packet_throughput)

            print("Acknowledgment Number Received: ", sequence_number)
        except timeout:
            print("A timeout occured. Resending the packet")
            resending_flag = True
            number_of_packets_lost += 1
            continue
    total_packets = i
        
stop_and_wait()

print("Number of packets lost", number_of_packets_lost)
# average_packet_delay_rounded = round(sum(packet_delays) / len(packet_delays))
# average_packet_delay_not_rounded = sum(packet_delays) / len(packet_delays)
# average_packet_throughput = round(sum(packet_throughputs) / len(packet_throughputs))
# performance = math.log(average_packet_throughput, 10) - math.log(average_packet_delay_not_rounded, 10)

# print("\n")
# print("Average Throughput", average_packet_throughput, "bits per second")
# print("Average Delay for Packets:", average_packet_delay_rounded, "milliseconds")
# print("Performance:", performance)
print("\n")

# packets_x = list(range(1, total_packets ))
# plt.plot(packets_x, packet_delays)

# plt.xlabel('Packets')
# plt.ylabel('Delay')
# plt.title('per-packet delays')
# plt.show()

# plt.plot(packets_x, packet_throughputs)
# plt.xlabel('Packets')
# plt.ylabel('Throughput')
# plt.title('per-packet throughput')
# plt.show()