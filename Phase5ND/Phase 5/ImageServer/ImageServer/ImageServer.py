import socket
import random

server_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("",server_port))
print("The server is ready to receive.\n")

image_reconstruct = []

def Create_checksum(packet, sequence_number):  
    # Split the bytes into a list of integers
    packet_ints = [int.from_bytes(packet[i:i+2], byteorder='big') for i in range(0, len(packet), 2)]
    
    # Add the sequence number to the sum of every two integers in the list
    sum_result = sum(packet_ints[i] + packet_ints[i+1] 
    if i+1 < len(packet_ints) 
    else packet_ints[i] 
    for i in range(0, len(packet_ints), 2)) + sequence_number
    
    # Take the one's complement of the sum
    check_sum = ~sum_result & 0xFFFF
    
    return check_sum

    # -----Manual corruption for Options 3/5-----
    # Options 2/4 must be "if percent_check != 0:"
    # Options 3/5 must be "if percent_check < [9 -> 2 in decrements of 0.5]
    # 9 = 0% chance
    # 2 = 70% chance
def Corrupt_data(data, seq_num):
    percent_check = random.randint(0,9)
    if percent_check != 0: # Simulate % of corruption
        return Create_checksum(data, seq_num)
    else:
        # Simulate a bit error in the checksum
        data_int = int.from_bytes(data, "big")
        num_bits = data_int.bit_length()
        num_bytes = (num_bits + 7) // 8
        bit = 1 << random.randint(0, num_bits-1)
        data_int = data_int ^ bit
        data = data_int.to_bytes(num_bytes, "big")
        calculated_checksum = Create_checksum(data, seq_num)
        return calculated_checksum

# Listen for client to tell us what option we have selected
option_one_chose = False
while True:
    message_from_client, client_address = server_socket.recvfrom(2048)
    if(message_from_client == b"op1"):
        option_one_chose = True
        break
    else:
        option_one_chose = False
        break

packet_num = 0
expected_seg_num = 0
input_count = 0
last_succesful_ack = 0

while True: # Continuous loop to read data from the client
    packet, client_address = server_socket.recvfrom(2048)
    packet_num +=1
    print(f"Waiting on packet {packet_num}...")

    if packet == b"end":
        print("Transmisison finished")
        break
    
    # Extract the sequence number and checksum from the packet
    seq_num = int.from_bytes(packet[0:2], byteorder = 'big')
    checksum = packet[2:4]
    data = packet[4:]
    
    print("Sent sequence number: ", seq_num)
    print("Expected seq number: ", expected_seg_num)

    # Condition to check for when option one is chosen
    if(option_one_chose == True):
        print(f"Option 1 has been chosen.")
        calculated_checksum = Create_checksum(data, seq_num)
        print(f"calculated_checksum = {calculated_checksum}")
    else:
        print(f"Options 2-5 has been chosen.")
        calculated_checksum = Corrupt_data(data, seq_num)
        print(f"calculated_checksum = {calculated_checksum}")
    
    checksum = int.from_bytes(checksum, "big")

    # Check the checksum with our incoming packet, if there is a mismatch we need to call for the packet to be resent
    # We do not proceed forward until a succesful packet is recieved
    if(calculated_checksum != checksum):
        print("Checksum from client: ", checksum)
        print("Checksum produced by the server: ", calculated_checksum)
        print("The packet recieved has a checksum mismatch")
        #print("The packet recieved has a checksum mismatch, requesting a new packet...")
        '''
        #resend last succesful ack
        message = b"ack"
        seq_num_str = str(last_succesful_ack)
        seq_num_byte = seq_num_str.encode()
        message = message + seq_num_byte
        server_socket.sendto(message, client_address)
        message = b"nak"
        server_socket.sendto(message, client_address)
        print("New packet request sent!")
        print(f"Resending ack: {last_succesful_ack}\n")
        expected_seg_num = last_succesful_ack
        '''
    else:
        # If our sequence don't match incoming to expected, after passing the checksum then we know
        # the client is asking for the ack back to move forward.

        # If the sequence numbers are different after passing the checksum we know that we can process the
        # packet and move forward

        if(seq_num != expected_seg_num):
            # Resend ACK with failed seq number
            print("Sequence numbers do not match, ACK must be resent!")
            message = b"ack"
            seq_num_str = str(seq_num)
            seq_num_byte = seq_num_str.encode()
            message = message + seq_num_byte
            server_socket.sendto(message, client_address)
        else:
            # We know we can move forward as expected sequence number matches the current sequence number
            # Now we will prepare for the next packet sequence number
            print("Seq match and Checksum match!")
            
            
            # Add the packet and sequence number to our imageReconstruct list
            input_count += 1
            print("Packets added to image: ", input_count)
            image_reconstruct.append((data))

            # Print out the packet and sequence number
            print(f"Packet {packet_num} has been received from the client.")
            print("Checksum that came with the packet: ", checksum)
            print("Checksums calculated in server: ", calculated_checksum)
            print("-" * 100 + '\n')
            # Tell the client that we have processed the packet and attach the sequence number with it
            message = b"ack"
            seq_num_str = str(expected_seg_num)
            seq_num_byte = seq_num_str.encode()
            message = message + seq_num_byte
            server_socket.sendto(message, client_address)
            expected_seg_num += 1
            #expected_seg_num = seq_num + 1


# Put together our fixed image
print("Now process the packets and construct the new image file.\n")
with open("received1_image.jpg", "wb") as file:
    for packet in image_reconstruct:
        file.write(packet)

server_socket.close()