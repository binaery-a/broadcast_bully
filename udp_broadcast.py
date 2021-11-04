"""
This is a class: UDP Broadcast Protocol.
Contains methods to make a connection, receive a datagram
"""
import socket

class UDPBroadcastProtocol:
    def __init__(self, message, decode_msg, state):
        """
            Method that initializes object attributes
        """
        self.message = message
        self.state = state
        self.decode_msg = decode_msg
        self.transport = None

    def connection_made(self, transport):
        """
        Method to make socket connection and use the broadcast protocol
        Accepts: transport object
        Returns: nothing, it connects to a socket with the broadcast protocol
        """
        self.transport = transport
        sock = transport.get_extra_info("socket") 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

    def datagram_received(self, data, addr):
        """
        Method to call decode message and pass datagram and address
        Accepts: data object and address object
        Returns: nothing, it calls decode_msg()
        """
        self.decode_msg(data, self.state)

    def error_received(self, exc):
        """
        Method to print to console if called. This function is not used.
        Accepts: exc object
        Returns: nothing, it prints to the console when called
        """
        print('Error received:', exc)

    def connection_lost(self, exc):
        """
        Method if connection lost, this function is not used.
        """
        pass
