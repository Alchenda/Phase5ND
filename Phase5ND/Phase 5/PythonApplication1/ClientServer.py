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
       return True
       #print(f"ACK Corrupted!")
    else:
        server_message = server_message
        return False
        #print(f"ACK Received!")
    return server_message

def ACK_loss(percentage_loss, server_message):
    if random.randint(1, 100) <= int(percentage_loss):
        print("ACK packet lost!")
        return True
        #return b""
    else:
        return False
        #return server_message

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
    TIMEOUT = 0.05
    total_start_time = time.time()
    base = 0 #base packet
    timer = 0
    start_timer = True
    elapsed_time = 0
    out_going_packets = [None] * len(output_image)
    #out_going_packets = []
    timer_array = [None] * len(output_image)
    num_of_packets_to_send = len(output_image)
    num_ack = 0
    window_size = 10 #establish the size of the sliding window
    client_socket.settimeout(TIMEOUT)
    print(f"This is how many packets need to be sent: {num_of_packets_to_send}")
    #this will continue looping until our transmission sequence is completely finished
    while True:

        #create our breakout/end transmission condition
        if(seq_num >= len(output_image)):
           print("Client has succesfully processed all of the packets to the server")
           break

        #load the data
        #we need to move through our entire window and send all of our data out
        while seq_num < base + window_size:

            if(seq_num >= len(output_image)): # we are are the end of our file we mist avoid indexing issues
                break

            packet = output_image[seq_num]

            #create our packet to be sent out
            check_sum = Create_checksum(packet, seq_num)
            check_sum = check_sum.to_bytes(2, "big")
            packet = check_sum + packet
            packet = seq_num.to_bytes(2, "big") + packet

            #store each of these packets in an array
            out_going_packets[seq_num] = packet

            #send out the packet
            Udt_send_packet(out_going_packets[seq_num])
            print(f"Sending packet {seq_num} from the SEND PACKET CONDTION")
            seq_num += 1

        #start our timer if appropriate
        if start_timer:
            timer = time.time()
            start_timer = False

        try:
            #pull the message from the server, as well as saving the address it has come from
            message_from_server, server_address = client_socket.recvfrom(2048)

            #change the message from bytes to a string to make operations easier
            str_message = message_from_server.decode()
            print(f"message from the server {str_message}")
            iso_str_message = str_message[:3] #isolate the ack or nak
            if(iso_str_message == "ack"):
                num_ack = int(str_message[3:]) #get the last number from the ack
                print(f"Extracted integer: {num_ack}, the base we are expecting: {base}")
                if num_ack == base:
                    timer = time.time()
                    base = num_ack + 1
                    #del out_going_packets[0]
        #our timeout procedure 
        except:
            
            if time.time() - timer > TIMEOUT:
                print("**** TIMEOUT ****")
                iteration = 0
                while iteration < len(out_going_packets):
                    Udt_send_packet(out_going_packets[iteration])
                    iteration += 1
                
                timer = time.time()

    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")


#**** Option 2 - ACK Corruption ****
elif(option_choice == "Option 2" or option_choice == "option 2"):
    print("Implementation of ACK corruption\n")
    count = 0
    seq_num = 0
    TIMEOUT = 0.05
    total_start_time = time.time()
    base = 0 #base packet
    timer = 0
    start_timer = True
    elapsed_time = 0
    out_going_packets = []
    timer_array = [None] * len(output_image)
    num_of_packets_to_send = len(output_image)
    num_ack = 0
    window_size = 10 #establish the size of the sliding window
    client_socket.settimeout(TIMEOUT)
    print(f"This is how many packets need to be sent: {num_of_packets_to_send}")
    while True:
        percent_error = input("Please select the percentage of ACK corruption you would like to be implemented(0-60 increments of 5 is the range): ")
        if percent_error in ["0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"]:
            break
        else:
            print("Invalid value, try again.")

    #this will continue looping until our transmission sequence is completely finished
    while True:

        #create our breakout/end transmission condition
        if(seq_num >= len(output_image)):
           print("Client has succesfully processed all of the packets to the server")
           break

        #load the data
        #we need to move through our entire window and send all of our data out
        while seq_num < base + window_size:

            if(seq_num >= len(output_image)): # we are are the end of our file we mist avoid indexing issues
                break

            packet = output_image[seq_num]

            #create our packet to be sent out
            check_sum = Create_checksum(packet, seq_num)
            check_sum = check_sum.to_bytes(2, "big")
            packet = check_sum + packet
            packet = seq_num.to_bytes(2, "big") + packet

            #store each of these packets in an array
            out_going_packets.append(packet)

            #send out the packet
            Udt_send_packet(out_going_packets[seq_num % window_size])
            print(f"Sending packet {seq_num} from the SEND PACKET CONDTION")
            seq_num += 1

        #start our timer if appropriate
        if start_timer:
            timer = time.time()
            start_timer = False

        try:
            #pull the message from the server, as well as saving the address it has come from
            message_from_server, server_address = client_socket.recvfrom(2048)

            #change the message from bytes to a string to make operations easier
            str_message = message_from_server.decode()
            #client_socket.settimeout(None) #allow timer to only be active during receiving
            print(f"message from the server {str_message}")
            iso_str_message = str_message[:3] #isolate the ack or nak
            #check for corruption, if corruption then we need to timeout. Treat corruption and nak the same
            if(not ACK_corruption(percent_error, message_from_server) and iso_str_message == "ack"):
                num_ack = int(str_message[3:]) #get the last number from the ack
                print(f"Extracted integer: {num_ack}, the base we are expecting: {base}")
                if num_ack == base:
                    timer = time.time()
                    base = num_ack + 1
                    del out_going_packets[0]
        #our timeout procedure 
        except:
            
            if time.time() - timer > TIMEOUT:
                print("**** TIMEOUT ****")
                iteration = 0
                while iteration < len(out_going_packets):
                    Udt_send_packet(out_going_packets[iteration])
                    iteration += 1
                
                timer = time.time()
    
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")
            
#**** Option 3 - DATA Corruption ****
# We are just going to send the packet to the server.
# Server will be responsible for corrupting the data portion of the packet
elif(option_choice == "Option 3" or option_choice == "option 3"):
    print("Implementation of DATA corruption\n")
    count = 0
    seq_num = 0
    TIMEOUT = 0.05
    total_start_time = time.time()
    base = 0 #base packet
    timer = 0
    start_timer = True
    elapsed_time = 0
    out_going_packets = []
    timer_array = [None] * len(output_image)
    num_of_packets_to_send = len(output_image)
    num_ack = 0
    window_size = 10 #establish the size of the sliding window
    client_socket.settimeout(TIMEOUT)
    print(f"This is how many packets need to be sent: {num_of_packets_to_send}")
    while True:
        percent_error = input("Please select the percentage of ACK corruption you would like to be implemented(0-60 increments of 5 is the range): ")
        if percent_error in ["0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"]:
            break
        else:
            print("Invalid value, try again.")

    #this will continue looping until our transmission sequence is completely finished
    while True:

        #create our breakout/end transmission condition
        if(seq_num >= len(output_image)):
           print("Client has succesfully processed all of the packets to the server")
           break

        #load the data
        #we need to move through our entire window and send all of our data out
        while seq_num < base + window_size:

            if(seq_num >= len(output_image)): # we are are the end of our file we mist avoid indexing issues
                break

            packet = output_image[seq_num]

            #create our packet to be sent out
            check_sum = Create_checksum(packet, seq_num)
            check_sum = check_sum.to_bytes(2, "big")
            packet = check_sum + packet
            packet = seq_num.to_bytes(2, "big") + packet

            #store each of these packets in an array
            out_going_packets.append(packet)

            #send out the packet
            Udt_send_packet(out_going_packets[seq_num % window_size])
            print(f"Sending packet {seq_num} from the SEND PACKET CONDTION")
            seq_num += 1

        #start our timer if appropriate
        if start_timer:
            timer = time.time()
            start_timer = False

        try:
            #pull the message from the server, as well as saving the address it has come from
            message_from_server, server_address = client_socket.recvfrom(2048)

            #change the message from bytes to a string to make operations easier
            str_message = message_from_server.decode()
            #client_socket.settimeout(None) #allow timer to only be active during receiving
            print(f"message from the server {str_message}")
            iso_str_message = str_message[:3] #isolate the ack or nak
            #check for corruption, if corruption then we need to timeout. Treat corruption and nak the same
            if(not ACK_corruption(percent_error, message_from_server) and iso_str_message == "ack"):
                num_ack = int(str_message[3:]) #get the last number from the ack
                print(f"Extracted integer: {num_ack}, the base we are expecting: {base}")
                if num_ack == base:
                    timer = time.time()
                    base = num_ack + 1
                    del out_going_packets[0]
        #our timeout procedure 
        except:
            
            if time.time() - timer > TIMEOUT:
                print("**** TIMEOUT ****")
                iteration = 0
                while iteration < len(out_going_packets):
                    Udt_send_packet(out_going_packets[iteration])
                    iteration += 1
                
                timer = time.time()

    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

#**** Option 4 - ACK packet loss ****
elif(option_choice == "Option 4" or option_choice == "option 4"):
    print("Implementation of ACK packet loss\n")
    count = 0
    seq_num = 0
    TIMEOUT = 0.05
    total_start_time = time.time()
    base = 0 #base packet
    timer = 0
    start_timer = True
    elapsed_time = 0
    out_going_packets = []
    timer_array = [None] * len(output_image)
    num_of_packets_to_send = len(output_image)
    num_ack = 0
    window_size = 10 #establish the size of the sliding window
    client_socket.settimeout(TIMEOUT)
    print(f"This is how many packets need to be sent: {num_of_packets_to_send}")
    while True:
        percent_error = input("Please select the percentage of ACK packet loss you would like to be implemented(0-60 increments of 5 is the range): ")
        if percent_error in ["0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"]:
            break
        else:
            print("Invalid value, try again.")

    #this will continue looping until our transmission sequence is completely finished
    while True:

        #create our breakout/end transmission condition
        if(seq_num >= len(output_image)):
           print("Client has succesfully processed all of the packets to the server")
           break

        #load the data
        #we need to move through our entire window and send all of our data out
        while seq_num < base + window_size:

            if(seq_num >= len(output_image)): # we are are the end of our file we mist avoid indexing issues
                break

            packet = output_image[seq_num]

            #create our packet to be sent out
            check_sum = Create_checksum(packet, seq_num)
            check_sum = check_sum.to_bytes(2, "big")
            packet = check_sum + packet
            packet = seq_num.to_bytes(2, "big") + packet

            #store each of these packets in an array
            out_going_packets.append(packet)

            #send out the packet
            Udt_send_packet(out_going_packets[seq_num % window_size])
            print(f"Sending packet {seq_num} from the SEND PACKET CONDTION")
            seq_num += 1

        #start our timer if appropriate
        if start_timer:
            timer = time.time()
            start_timer = False

        try:
            #pull the message from the server, as well as saving the address it has come from
            message_from_server, server_address = client_socket.recvfrom(2048)

            #message_from_server = ACK_loss(percent_error, server_message)

            #change the message from bytes to a string to make operations easier
            str_message = message_from_server.decode()
            #client_socket.settimeout(None) #allow timer to only be active during receiving
            print(f"message from the server {str_message}")
            iso_str_message = str_message[:3] #isolate the ack or nak
            #check for corruption, if corruption then we need to timeout. Treat corruption and nak the same
            if(not ACK_loss(percent_error, message_from_server) and iso_str_message == "ack"):
                num_ack = int(str_message[3:]) #get the last number from the ack
                print(f"Extracted integer: {num_ack}, the base we are expecting: {base}")
                if num_ack == base:
                    timer = time.time()
                    base = num_ack + 1
                    del out_going_packets[0]
        #our timeout procedure 
        except:
            
            if time.time() - timer > TIMEOUT:
                print("**** TIMEOUT ****")
                iteration = 0
                while iteration < len(out_going_packets):
                    Udt_send_packet(out_going_packets[iteration])
                    iteration += 1
                
                timer = time.time()
            
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

#**** Option 5 - Data packet loss ****
elif(option_choice == "Option 5" or option_choice == "option 5"):
    print("Implementation of Data packet loss\n")
    count = 0
    seq_num = 0
    TIMEOUT = 0.05
    total_start_time = time.time()
    base = 0 #base packet
    timer = 0
    start_timer = True
    elapsed_time = 0
    out_going_packets = []
    timer_array = [None] * len(output_image)
    num_of_packets_to_send = len(output_image)
    num_ack = 0
    window_size = 10 #establish the size of the sliding window
    client_socket.settimeout(TIMEOUT)
    print(f"This is how many packets need to be sent: {num_of_packets_to_send}")
    
    while True:
        percentage_loss = input("Please select the percentage chance of Data packet loss you would like to be implemented(0-60 increments of 5 is the range): ")
        if percentage_loss == 0 or 5 or 10 or 15 or 20 or 25 or 30 or 35 or 40 or 45 or 50 or 55 or 60:
            break
        else:
            percentage_loss = input("invalid value, try again")
    

    #this will continue looping until our transmission sequence is completely finished
    while True:

        #create our breakout/end transmission condition
        if(seq_num >= len(output_image)):
           print("Client has succesfully processed all of the packets to the server")
           break

        #load the data
        #we need to move through our entire window and send all of our data out
        while seq_num < base + window_size:

            if(seq_num >= len(output_image)): # we are are the end of our file we mist avoid indexing issues
                break

            packet = output_image[seq_num]

            #create our packet to be sent out
            check_sum = Create_checksum(packet, seq_num)
            check_sum = check_sum.to_bytes(2, "big")
            packet = check_sum + packet
            packet = seq_num.to_bytes(2, "big") + packet

            #store each of these packets in an array
            out_going_packets.append(packet)

            #send out the packet
            data_loss_chance = data_loss(percentage_loss, out_going_packets[seq_num % window_size])
            Udt_send_packet(data_loss_chance)
            print(f"Sending packet {seq_num} from the SEND PACKET CONDTION")
            seq_num += 1

        #start our timer if appropriate
        if start_timer:
            timer = time.time()
            start_timer = False

        try:
            #pull the message from the server, as well as saving the address it has come from
            message_from_server, server_address = client_socket.recvfrom(2048)

            #message_from_server = ACK_loss(percent_error, server_message)

            #change the message from bytes to a string to make operations easier
            str_message = message_from_server.decode()
            #client_socket.settimeout(None) #allow timer to only be active during receiving
            print(f"message from the server {str_message}")
            iso_str_message = str_message[:3] #isolate the ack or nak
            #check for corruption, if corruption then we need to timeout. Treat corruption and nak the same
            if(iso_str_message == "ack"):
                num_ack = int(str_message[3:]) #get the last number from the ack
                print(f"Extracted integer: {num_ack}, the base we are expecting: {base}")
                if num_ack == base:
                    timer = time.time()
                    base = num_ack + 1
                    del out_going_packets[0]
        #our timeout procedure 
        except:
            
            if time.time() - timer > TIMEOUT:
                print("**** TIMEOUT ****")
                iteration = 0
                while iteration < len(out_going_packets):
                    Udt_send_packet(out_going_packets[iteration])
                    iteration += 1
                
                timer = time.time()
            
            
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    print(f"\n---Total Completion Time: {elapsed_time: .10f} seconds.---\n")

# ************ End of Options Implementation ************

final_message = b"end"
client_socket.sendto(final_message, (server_name, client_port))
#print("Packets sent:", count)
print("All packets sent.\nShutting down client...")
client_socket.close()