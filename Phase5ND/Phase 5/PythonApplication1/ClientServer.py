from logging.config import valid_ident
import socket
import random
import time

# ************ Function definitions ************

def Make_packet(file_to_read):
    # All of the packets that we are going to send out
    packets_to_send = []
    # Open our file that is in the same directory of our python script
    with open(file_to_read, "rb") as file:
        # Indefinitely loop our file
        while True:
            packet = file.read(1024)
            # Once we have reached the end of our .bmp file, we need to exit our while loop
            if not packet:
                break
            packets_to_send.append(packet)

    return packets_to_send

def Create_checksum(packet, sequence_number):  
    # Split the bytes into a list of integers
    packet_ints = [int.from_bytes(packet[i:i+2], byteorder='big') for i in range(0, len(packet), 2)]
    
    # Add the sequence number to the sum of every two integers in the list
    sum_result = sum(packet_ints[i] + packet_ints[i+1] for i in range(0, len(packet_ints), 2)) + sequence_number
    
    # Take the one's complement of the sum
    check_sum = ~sum_result & 0xFFFF
    
    return check_sum

def Udt_send_packet(packet):
    server_name = socket.gethostname()
    clientPort = 12000
    client_socket.sendto(packet, (server_name, clientPort))

def ACK_corruption(percent_error, server_message):
    # Create our error range
    percent_error = int(percent_error)
    ack_error = random.randint(0, 99)

    if(ack_error > percent_error):
        ack_error = 0
    else:
        ack_error = 1

    # Corrupt the ack message
    if ack_error == 1:
       server_message = b"x" + server_message
       print(f"ACK Corrupted!")
    else:
        server_message = server_message
        print(f"ACK Received!")
    return server_message

def ACK_loss(percentage_loss, server_message):
    if random.randint(1, 100) <= int(percentage_loss):
        print("ACK packet lost!")
        return b""
    else:
        return server_message

def data_loss(percentage_loss, packet_to_send):
    # Determine whether to drop the packet
    if random.random() < int(percentage_loss) / 100:
        print("Dropping data packet...")
        # Randomly drop a percentage of the data bytes in the packet
        data = packet_to_send[3:] # Extracting only the data bytes
        num_bytes_to_drop = int(len(data) * int(percentage_loss) / 100)
        if num_bytes_to_drop > 0: # Selects a random index in the data to drop
            start_index = random.randint(0, len(data) - num_bytes_to_drop)
            end_index = start_index + num_bytes_to_drop
            dropped_data = data[start_index:end_index]
            packet_to_send = packet_to_send[:3] + dropped_data + packet_to_send[3+end_index:]
            print(f"Data Dropped!")
    return packet_to_send

# ************ End of Function definitions ************

# Setup the client UDP
# We will use a generic establishment, thus will work on any PC.
server_name = socket.gethostname()
print(f"Host client name: {server_name}")
server_host_ip = socket.gethostbyname(server_name)
print(f"Host server IP: {server_host_ip}")
HOST = server_host_ip
client_port = 12000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Client is now connected to the server!")

#source of image: https://people.math.sc.edu/Burkardt/data/bmp/bmp.html

file_name = "FattestCatEver.jpg"
output_image = Make_packet(file_name) # Calling out Make_packet function
count = 0
seq_num = 0
valid_input = False

# Use a switch to decide course of action based on user input.
while valid_input != True:

    # Create decision for the three options a user has for the packet development
    option_choice = input("Please choose an option in your option selection please match the casing of option names.\n \
    Option 1: No loss/bit-errors \n \
    Option 2: ACK packet bit-error \n \
    Option 3: Data packet bit-error\n \
    Option 4: ACK packet loss\n \
    Option 5: Data packet loss\n \
    ---Please do one or the other 'Option' or 'option'---\n>")
    
    if (option_choice == "Option 1" or option_choice == "option 1"):
        print("\n**** You have chosen option 1 ****")
        valid_input = True
        # Tell server our option selection
        server_message = b"op1"
        client_socket.sendto(server_message, (server_name, client_port))

    elif (option_choice == "Option 2" or option_choice == "option 2"):
        print("\n**** You have chosen option 2 ****")
        valid_input = True
        # Tell server our option selection
        server_message = b"op2"
        client_socket.sendto(server_message, (server_name, client_port))

    elif (option_choice == "Option 3" or option_choice == "option 3"):
        print("\n**** You have chosen option 3 ****")
        valid_input = True
        # Tell server our option selection
        server_message = b"op3"
        client_socket.sendto(server_message, (server_name, client_port))

    elif (option_choice == "Option 4" or option_choice == "option 4"):
        print("\n**** You have chosen option 4 ****")
        valid_input = True
        # Tell server our option selection
        server_message = b"op4"
        client_socket.sendto(server_message, (server_name, client_port))

    elif (option_choice == "Option 5" or option_choice == "option 5"):
        print("\n**** You have chosen option 5 ****")
        valid_input = True
        # Tell server our option selection
        server_message = b"op5"
        client_socket.sendto(server_message, (server_name, client_port))

    else:
        print("You have either entered an invalid option or did not match the option casing, try again\n")
        valid_input = False

# Packets are now in our output array.
# We will parse the array.

# ************ Options Implementation ************

# **** Option 1 - No Loss ****
if(option_choice == "Option 1" or option_choice == "option 1"):
    print("We will now transmit packets with absolutely no loss at any point.\n")
    count = 0
    seq_num = 0
    TIMEOUT = 0.03
    total_start_time = time.time()
    packet_num_sent_tracker = []
    packet_time_tracker = []
    window_size = 10
    timeout_occured = False

    while count < len(output_image):
        # Adds sequence number to packet and checksum, creating the header.
        timeout_occured = False
        packet = output_image[count]
        count += 1
        print(f"Packet: {count}\n")
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} check_sum = {check_sum}")

        check_sum = check_sum.to_bytes(2, "big")
        packet = check_sum + packet
        packet = seq_num.to_bytes(1, "big") + packet

        # Before we ever go to send anything, we need to do a timeout check to ensure no packet has expired
        if len(packet_num_sent_tracker) > 0:
            #go through all of our timer tracking for each packet
            for index, i in packet_time_tracker:
                    
                if time.time() - i < TIMEOUT: #this packet has not timed out, move on to the next packet to check
                    continue

                #this is the case where one of our packets has timed out, we need to move to this value and readjust everything for resending
                count = packet_num_sent_tracker[index] - 1
                print(f"Packet: {count}; Has timed out. Base pointer will now be readjusted and the new window will start at this packet")
                #since our base pointer is being changed we now need to dump both of our arrays and reset them
                packet_num_sent_tracker = []
                packet_time_tracker = []
                timeout_occured = True
                break


        # Send the packet to the server and store each packet number as it is sent, do not exceed our window limit, and ensure timeout has not occured
        if len(packet_num_sent_tracker) < window_size and timeout_occured != True:
            Udt_send_packet(packet)
            packet_num_sent_tracker.append(count)

            # Start Timer for individual packet and store it
            #start_time = time.time()
            packet_time_tracker.append(time.time())
            print(f"Packet {count} has been sent to the server...")

        # If our tracker is the length of our window size, we do not want to move on to the next packet, we want to just keep polling the server for responses
        # until we can either dump a packet or have to reset due to now ack back
        while len(packet_num_sent_tracker) >= window_size and timeout_occured != True:

            # Receive message from server
            message_from_server, server_address = client_socket.recvfrom(2048)
            message = message_from_server[:3].decode("utf-8")
            # if we do not get an ack, we need to check all of our times for the packets that have been sent 
            while message != "ack" and timeout_occured != True:
                #go through all of our timer tracking for each packet
                for index, i in packet_time_tracker:
                    
                    if time.time() - i < TIMEOUT: #this packet has not timed out, move on to the next packet to check
                        continue

                    #this is the case where one of our packets has timed out, we need to move to this value and readjust everything for resending
                    count = packet_num_sent_tracker[index] - 1
                    print(f"Packet: {count}; Has timed out. Base pointer will now be readjusted and the new window will start at this packet")
                    #since our base pointer is being changed we now need to dump both of our arrays and reset them
                    packet_num_sent_tracker = []
                    packet_time_tracker = []
                    timeout_occured = True
                    break

                message_from_server = ""
                message_from_server, server_address = client_socket.recvfrom(2048)

            # Below is what if we get an ack back and there is no timeout, if this does occur after we perform the operation we will jump out of our while loop
            # And send another packet
            if timeout_occured != True:
                int_read = message_from_server[3:].decode("utf-8")
                #remove the time of the ack'd packet in the timer buffer for individual packets
                packet_time_tracker.remove(packet_num_sent_tracker.index(int_read))
                #remove the packet from the sent packet buffer since it no longer needs checking
                packet_num_sent_tracker.remove(int_read)
        
'''
    for packet in output_image:
        # Adds sequence number to packet and checksum, creating the header.
        count += 1
        print(f"Packet: {count}\n")
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} check_sum = {check_sum}")

        check_sum = check_sum.to_bytes(2, "big")
        packet = check_sum + packet
        packet = seq_num.to_bytes(1, "big") + packet

        # Send the packet to the server and store each packet number as it is sent, do not exceed our window limit

        # If our tracker is the length of our window size, we do not want to move on to the next packet
        while len(packet_num_sent_tracker) > window_size:

        if len(packet_num_sent_tracker) < window_size:
            Udt_send_packet(packet)
            packet_num_sent_tracker.append(count)

            # Start Timer for individual packet and store it
            #start_time = time.time()
            packet_time_tracker.append(time.time())
            print(f"Packet {count} has been sent to the server...")
        
        # Receive message from server
        message_from_server, server_address = client_socket.recvfrom(2048)

        # We now must wait for our server to tell us that it has processed our packet and then we can move on to our next packet
        while message_from_server[:3] != b"ack":
            if time.time() - start_time > TIMEOUT:
                print(f"Timeout. Resending packet {count}...")
                Udt_send_packet(packet)
                print(f"Packet {count} is resending...")
                start_time = time.time()
            message_from_server = ""
            message_from_server, server_address = client_socket.recvfrom(2048)
'''
        packet_elapsed_time = time.time() - start_time
        print(f"Packet finished transmitting.")
        print(f"Packet {count} elapsed time = {packet_elapsed_time: .15f} seconds to receive ACK.\n")
        print("-" * 100 + '\n')
        seq_num = (seq_num +1) % 2 # Using mod to make sure sequence number stays 0/1

    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")


#**** Option 2 - ACK Corruption ****
elif(option_choice == "Option 2" or option_choice == "option 2"):
    print("Implementation of ACK corruption\n")
    count = 0
    seq_num = -1
    TIMEOUT = 0.03
    total_start_time = time.time()
    
    while True:
        percent_error = input("Please select the percentage of ACK corruption you would like to be implemented(0-60 increments of 5 is the range): ")
        if percent_error == 0 or 5 or 10 or 15 or 20 or 25 or 30 or 35 or 40 or 45 or 50 or 55 or 60:
            break
        else:
            percent_error = input("Invalid value, try again.")

    for packet in output_image:
        count += 1
        print(f"Packet: {count}\n")
        # Create the header for the packet
        seq_num = (seq_num +1) % 2
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} check_sum: {check_sum}")

        check_sum = check_sum.to_bytes(2, "big")
        header = seq_num.to_bytes(1, "big") + check_sum

        # Attach header to packet
        packet_to_send = header + packet

        ack_corruption = ACK_corruption(percent_error, packet_to_send)

        # Send the packet to the server
        Udt_send_packet(ack_corruption)

        # Start timer
        start_time = time.time()
        # Listen for message back from server
        message_from_server = ""
        message_from_server, server_address = client_socket.recvfrom(2048)

        while message_from_server != b"ack":
            if time.time() - start_time < TIMEOUT:
                # Our timer has not timed out yet, we need to wait until our timer has timed out to resend our packet.
                # In the case of no timeout, we want to continue listening for a message back from the server.
                continue

            else:
                # Treat NAK and corruption the same
                print("The previous packet either had corruption, or the ACK/NAK message could not be processed.")
                print(f"\nThe packet {count} will be resent.")

                # Create the header for the packet
                check_sum = Create_checksum(packet, seq_num)
                print(f"\nResent packet {count} check_sum: {check_sum}")
                check_sum = check_sum.to_bytes(2, "big")
                header = seq_num.to_bytes(1, "big") + check_sum

                # Attach header to packet
                packet_to_send = header + packet
                ack_corruption = ACK_corruption(percent_error, packet_to_send)
                # Resend the packet to the server
                Udt_send_packet(ack_corruption)
                #count += 1

                # Start timer
                start_time = time.time()
                
            # Wait for server response
            message_from_server = ""
            message_from_server, serverAddress = client_socket.recvfrom(2048)
            
            if(message_from_server == b"ack"):
                count - 1
                print(f"Packet {count} sent without corruption in DATA and no corruption in ACK.\n")
                break
                
        packet_elapsed_time = time.time() - start_time
        print(f"Packet finished transmitting.")
        print(f"Packet {count} elapsed time = {packet_elapsed_time: .15f} seconds.")
        print("-" * 100 + '\n')

    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")
            
#**** Option 3 - ACK Corruption ****
# We are just going to send the packet to the server.
# Server will be responsible for corrupting the data portion of the packet
elif(option_choice == "Option 3" or option_choice == "option 3"):
    print("Server-side data corruption\n")
    count = 0
    seq_num = -1
    TIMEOUT = 0.03
    total_start_time = time.time()

    for packet in output_image:
        count += 1
        print(f"Packet: {count}\n")
        # Create the header for the packet
        seq_num = (seq_num +1) % 2
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} check_sum: {check_sum}")

        check_sum = check_sum.to_bytes(2, "big")
        header = seq_num.to_bytes(1, "big") + check_sum

        # Attach header to packet
        packet_to_send = header + packet

        # Send the packet to the server

        Udt_send_packet(packet_to_send)

        # Start Timer
        start_time = time.time()

        # Listen for message back from server
        message_from_server = ""
        message_from_server, serverAddress = client_socket.recvfrom(2048)

        while message_from_server != b"ack":
            if time.time() - start_time > TIMEOUT:
                print(f"Timeout. Resending packet {count}...")
                Udt_send_packet(packet)
                print(f"Packet {count} is resending...")
                start_time = time.time()
            else:
                # Treat NAK and corruption the same
                print("\nThe previous packet had corruption in the data.")
                print(f"The packet {count} will be resent")

                # Create the header for the packet
                check_sum = Create_checksum(packet, seq_num)
                print(f"\nResent packet {count} check_sum: {check_sum}")
                check_sum = check_sum.to_bytes(2, "big")
                header = seq_num.to_bytes(1, "big") + check_sum

                # Attach header to packet
                packet_to_send = header + packet

                # Resend the packet to the server
                Udt_send_packet(packet_to_send)
                #count += 1
                start_time = time.time()

            # Wait for server response
            message_from_server = ""
            message_from_server, server_address = client_socket.recvfrom(2048)

            if(message_from_server == b"ack"):
                count - 1
                print(f"Packet {count} sent without corruption in DATA.\n")

        packet_elapsed_time = time.time() - start_time
        print(f"Packet finished transmitting.")
        print(f"Packet {count} elapsed time = {packet_elapsed_time: .15f} seconds.")
        print("-" * 100 + '\n')

    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

#**** Option 4 - ACK packet loss ****
elif(option_choice == "Option 4" or option_choice == "option 4"):
    print("Implementation of ACK packet loss\n")
    count = 0
    seq_num = -1
    TIMEOUT = 0.03
    total_start_time = time.time()
    
    while True:
        percentage_loss = input("Please select the percentage chance of ACK packet loss you would like to be implemented(0-60 increments of 5 is the range): ")
        if percentage_loss == 0 or 5 or 10 or 15 or 20 or 25 or 30 or 35 or 40 or 45 or 50 or 55 or 60:
            break
        else:
            percentage_loss = input("invalid value, try again")

    for packet in output_image:
        count += 1
        print(f"Packet: {count}\n")
        # Create the header for the packet
        seq_num = (seq_num +1) % 2
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} Checksum: {check_sum}")

        check_sum = check_sum.to_bytes(2, "big")
        header = seq_num.to_bytes(1, "big") + check_sum

        # Attach header to packet
        packet_to_send = header + packet

        # Send the packet to the server
        Udt_send_packet(packet_to_send)

        # Start timer
        start_time = time.time()

        # Listen for message back from server
        message_from_server = ""
        message_from_server, server_address = client_socket.recvfrom(2048)

        message_from_server = ACK_loss(percentage_loss, message_from_server)

        while message_from_server != b"ack":
            if time.time() - start_time < TIMEOUT:
                # Our timer has not timed out yet, we need to wait until our timer has timed out to resend our packet.
                # In the case of no timeout, we want to continue listening for a message back from the server 
                continue
            else:
                # Our timer has timed out, we need to resend our packet and restart our timer
                print(f"Timeout. Resending packet {count}...")
                Udt_send_packet(packet_to_send)
                print(f"Packet {count} is resending...")
                print("Timer will now be reset")
                start_time = time.time()

                # Packet resent, we listen back for our message from the server
                print("Waiting for incoming message from the server")
                message_from_server = ""
                message_from_server, server_address = client_socket.recvfrom(2048)

                # Add our chance of artificial loss again
                message_from_server = ACK_loss(percentage_loss, message_from_server)

                if(message_from_server == b"ack"):

                    print(f"Packet {count} sent without corruption in DATA and no corruption in ACK\n")
                    break
             
        packet_elapsed_time = time.time() - start_time
        print(f"Packet finished transmitting.")
        print(f"Packet {count} elapsed time = {packet_elapsed_time: .15f} seconds.")
        print("-" * 100 + '\n')
            
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

#**** Option 5 - Data packet loss ****
elif(option_choice == "Option 5" or option_choice == "option 5"):
    print("Implementation of Data packet loss\n")
    count = 0
    seq_num = -1
    TIMEOUT = 0.03
    total_start_time = time.time()
    
    while True:
        percentage_loss = input("Please select the percentage chance of Data packet loss you would like to be implemented(0-60 increments of 5 is the range): ")
        if percentage_loss == 0 or 5 or 10 or 15 or 20 or 25 or 30 or 35 or 40 or 45 or 50 or 55 or 60:
            break
        else:
            percentage_loss = input("invalid value, try again")
    

    for packet in output_image:
        count += 1
        print(f"Packet: {count}\n")
        # Create the header for the packet
        seq_num = (seq_num +1) % 2
        check_sum = Create_checksum(packet, seq_num)
        print(f"Displaying checksums before errors/ack resending.")
        print(f"Packet {count} Checksum: {check_sum}")

        check_sum= check_sum.to_bytes(2, "big")
        header = seq_num.to_bytes(1, "big") + check_sum

        # Attach header to packet
        packet_to_send = header + packet

        # Adding the intentional data loss
        data_loss_chance = data_loss(percentage_loss, packet_to_send)

        # Send the packet to the server
        Udt_send_packet(data_loss_chance)

        # Start timer
        start_time = time.time()

        # Listen for message back from server
        message_from_server = ""
        message_from_server, server_address = client_socket.recvfrom(2048)

        while message_from_server != b"ack":
            if time.time() - start_time < TIMEOUT:
                # Our timer has not timed out yet, we need to wait until our timer has timed out to resend our packet.
                # In the case of no timeout, we want to continue listening for a message back from the server.
                continue
            else:
                # Our timer has timed out, we need to resend our packet and restart our timer
                print(f"Timeout. Resending packet {count}...")
                data_loss_chance = data_loss(percentage_loss, packet_to_send)
                Udt_send_packet(data_loss_chance)
                print(f"Packet {count} is resending...")
                print("Timer will now be reset")
                start_time = time.time()

                # Packet resent, we listen back for our message from the server
                print("Waiting for incoming message from the server")
                message_from_server = ""
                message_from_server, server_address = client_socket.recvfrom(2048)

                if (message_from_server == b"ack"):
                    print(f"Packet {count} sent without corruption in DATA and no corruption in ACK\n")
                    break

        packet_elapsed_time = time.time() - start_time
        print(f"Packet finished transmitting.")
        print(f"Packet {count} elapsed time = {packet_elapsed_time: .15f} seconds.")
        print("-" * 100 + '\n')
            
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

# ************ End of Options Implementation ************

final_message = b"end"
client_socket.sendto(final_message, (server_name, client_port))
print("Packets sent:", count)
print("All packets sent.\nShutting down client...")
client_socket.close()