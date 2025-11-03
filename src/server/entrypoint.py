
from src.common.network import Netsock
from src.common import packets
import struct
   
    

def server_main(ip: str, port: int):
    """
    Main Entrypoint for the server.
    """

    net = Netsock(ip, port)


    net.start_server()

    while net.is_open(): # blocks until the client disconnects!
        pass
