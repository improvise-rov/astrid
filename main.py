import sys

from src.common import consts
from src.poolside.entrypoint import poolside_main
from src.rov.entrypoint import rov_main

def extract_args() -> tuple[str, int, bool]:
    """
    loops over the list of arguments passed to the program and extracts data from them
    """

    ip = "127.0.0.1"
    port = 8080
    simulated_hardware = False

    for idx, arg in enumerate(sys.argv):
        if arg == '--ip': ip = sys.argv[idx + 1] # get the next arg
        if arg == '--port': port = int(sys.argv[idx + 1])
        if arg == '--simulated': simulated_hardware = True

    return ip, port, simulated_hardware

if __name__ == "__main__":
    print(consts.IMPROVISE_ASCII_ART_STRING)
    print(" -=- ASTRID -=- ")
    print()

    poolside = '--poolside' in sys.argv
    rov = '--rov' in sys.argv

    if poolside and rov:
        # if both cmdline flags are present, pretend neither are
        poolside = False
        rov = False

    ip, port, simulated_gpio = extract_args()

    if poolside:
        print("[poolside]")
        poolside_main(ip, port)
        exit()
    if rov:
        print("[rov]")
        rov_main(ip, port, simulated_gpio)
        exit()

    print("please use --poolside for the poolside xor --rov for the rov.")
    print("(using neither or both will result in this message)")
    exit(-1)