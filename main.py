import sys

from src.common import consts
from src.client.entrypoint import client_main
from src.server.entrypoint import server_main

"""
main program entrypoint.

the main purpose of this script is to extract arguments from the command line
and delegate to other parts of the program.

this might get rewritten, it feels kinda weird and jank right now, but idk.

- fynn
"""

def extract_args() -> tuple[str, int]:
    """
    loops over the list of arguments passed to the program and extracts data from them
    """

    ip = "127.0.0.1"
    port = 8080

    for idx, arg in enumerate(sys.argv):
        if arg == '--ip': ip = sys.argv[idx + 1] # get the next arg
        if arg == '--port': port = int(sys.argv[idx + 1])

    return ip, port

if __name__ == "__main__":
    print(consts.IMPROVISE_ASCII_ART_STRING)
    print(" -=- ASTRID -=- ")
    print()

    use_client = '--client' in sys.argv
    use_server = '--server' in sys.argv

    if use_client and use_server:
        # if both cmdline flags are present, pretend neither are
        use_client = False
        use_server = False

    ip, port = extract_args()

    if use_client:
        print("[client]")
        client_main(ip, port)
        exit()
    if use_server:
        print("[server]")
        server_main(ip, port)
        exit()

    print("please use --client for the client xor --server for the server.")
    print("(using neither or both will result in this message)")
    exit(-1)