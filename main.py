import sys

from src.common import consts
from src.poolside.entrypoint import poolside_main
from src.rov.entrypoint import rov_main

def extract_args(default_port: int, default_target_port: int) -> tuple[str, int, bool, int]:
    """
    loops over the list of arguments passed to the program and extracts data from them
    """

    target_ip = "127.0.0.1"
    target_port = default_target_port
    port = default_port
    simulated_hardware = False

    for idx, arg in enumerate(sys.argv):
        if arg == '--target-ip': target_ip = sys.argv[idx + 1] # get the next arg
        if arg == '--target-port': target_port = int(sys.argv[idx + 1])
        if arg == '--port': port = int(sys.argv[idx + 1])
        if arg == '--simulated': simulated_hardware = True

    return target_ip, target_port, simulated_hardware, port

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

    if poolside:
        print("[poolside]")
        target_ip, target_port, _, port = extract_args(8080, 8081)
        poolside_main(target_ip, target_port, port)
        exit()
    if rov:
        print("[rov]")
        target_ip, target_port, simulated_gpio, port = extract_args(8081, 8080)
        rov_main(target_ip, target_port, simulated_gpio, port)
        exit()

    print("please use --poolside for the poolside xor --rov for the rov.")
    print("(using neither or both will result in this message)")
    exit(-1)