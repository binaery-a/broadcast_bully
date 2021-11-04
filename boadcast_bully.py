import asyncio
import socket
import time
import pickle
import sys
from udp_broadcast import UDPBroadcastProtocol

"""
    Broadcast Bully:
        -an alternative to the classic Bully algorithm
        -uses the broadcast protocol to communicate with nodes in the network
        -sends and receives messages containing IP addresses, victory messages, electipon messages, and timerout messages
        -requires manual input (integer) from console for timeout period
        -timeout period is used to simulate a node failure
        -compares known IP addresses with its own and correctly elects a coordinator as nodes fail"
"""


def obtain_ip(state):
    """
    Method to get own ip address.
    Accepts: state which is an empty object from the udp_broadcast class
    Returns: ip address (string)
    """
    # gethostname() returns a string containing the hostname of the machine
    # gethostname() translates a host name to IPv4 address format
    state.my_ip = socket.gethostbyname(socket.gethostname())
    print("\nMy IP is:", state.my_ip, "\n")
    return state.my_ip


def decode_msg(data, state):
    """
    Method to decode a received message
    Accepts: state which is an empty object from the udp_broadcast class
             data which is a bytes object containing the incoming data
    Returns: nothing, it decodes a message and checks if it has victory in it
    """
    print("Received: Broadcast ", data.decode())

    # split the data string into a list
    # check the 0th element of data
    # set the coordinator using the 1st element of data
    if data.decode().split()[0] == "Victory":
        state.coordinator = data.decode().split()[1]
    else:
        state.nodes[data.decode()] = True

    print("My new coordinator is: ", state.coordinator)


async def election(state):
    """
    Async method to elect a coordinator
    Accepts: state which is an empty object from the udp_broadcast class
    Returns: nothing, it compares max key to its own, and broadcasts victory message with own IP 
        declaring victory over all nodes in network (known IPs)
    """
    await asyncio.sleep(10)
    # checks if nodes is not empty
    if state.nodes: 
        # determines the max key in nodes
        max_key = max(state.nodes)
        print("My new coordinator is:", max_key)

        # check if itself is the max key
        if (max_key == state.my_ip):
            print("I am coordinator..")
            # assigns IP to coodnator
            state.coordinator = state.my_ip
            # create victory message
            victory_message = "Victory " + state.coordinator
            # send encoded victory message
            state.current_transport.sendto(victory_message.encode())
    else:
        print("Nodes is empty...")
        

async def fail_detect(state):
    """
    Async method to detect a failure in a node (forced a failure to detect for testing)
    Accepts: state which is an empty object from the udp_broadcast class
    Returns: nothing, it pops nodes from dictionary if node fails and notifies if popped node is coordinator, coordinator failed
    """
    failed_key = None
    while True:
        # set each key to false, indicates has failed
        for k in state.nodes:
            state.nodes[k] = False
        await asyncio.sleep(10)

        for k in state.nodes:
            # check if false, indicates failure
            if state.nodes[k] == False:
                failed_key = k
        # if key has failed, remove the key from nodes with pop        
        if failed_key:
            state.nodes.pop(failed_key)
            failed_key = None
            # the coordinator is not in nodes, then it has failed, could have been popped
            if not (state.coordinator in state.nodes):
                print("Coordinator failed... Starting election...") 
                state.coordinator = None
                # call election to determine new coordinator
                asyncio.create_task(election(state))

async def beacon_broadcast(state):
    """
    Async method to broadcast messages
    Accepts: state which is an empty object from the udp_broadcast class
    Returns: nothing, it creates a datagram connection and allows for broadcast
    """
    # Get a reference to the event loop
    loop = asyncio.get_running_loop()
    message = obtain_ip(state)
 
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPBroadcastProtocol(message, decode_msg, state),
        local_addr=('255.255.255.255', 37020),
        remote_addr=('255.255.255.255', 37020),
        allow_broadcast=True)

    state.current_transport = transport

    while (state.broadcast == True):
        transport.sendto(message.encode())
        await asyncio.sleep(5)
        print("Broadcast state: ", state.broadcast)

    transport.close()


async def timeout(period, state):
    """
    Async method to set flag for broadcasting
    Accepts: period object from console input, and state which is an empty object from the udp_broadcast class
    Returns: nothing, it sets broadcast to false if called after timeout, simulating node failure
    """
    await asyncio.sleep(period)
    state.broadcast = False
    print("Node failed...")


async def main():
    """
    Async main method to initialize objects, get console input, and gather asycn methods to call and run asynchronously
    """
    state = type('', (), {})()
    state.nodes = {}
    state.broadcast = True
    state.coordinator = None
    state.my_ip = None
    state.current_transport = None

    period = int(sys.argv[1])
    print("Time period:", period)
    await asyncio.gather(
        election(state),
        timeout(period, state),
        beacon_broadcast(state),
        fail_detect(state),

        )


asyncio.run(main())
"""
    Async method to call main method to run asyncronously
"""
