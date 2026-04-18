import threading
import struct
from src.common import consts
from src.common.network import Netsock
from src.client.logger import Logger
from src.client.float import packets



class FloatInterface():
    """
    Interface to our float, Morag
    """
    POINT_FORMAT: str = ">ff"

    def __init__(self, ) -> None:
        self.net = Netsock(consts.FLOAT_IP, consts.FLOAT_PORT)
        self.profile_ready = False
        self.processed_data: list[tuple[float, float]] = []


    def run(self):
        Logger.log("attempting float process")
        process_thread = threading.Thread(target=self._run_thread_activity)
        process_thread.run()

    
    def consume_raw_data(self, data: bytes):
        points = struct.iter_unpack(FloatInterface.POINT_FORMAT, data)
        self.processed_data = []
        for datum in points:
            self.processed_data.append(
                (datum[0], datum[1])
            )

    def get_processed_data(self) -> list[tuple[float, float]]:
        return self.processed_data


    def _run_thread_activity(self):
        # connect
        connected = self.net.start_client()

        if not connected:
            Logger.log("float profile failed! (couldn't connect)")
            return
        
        if not self.profile_ready:

            # tell go down
            self.net.send(packets.START_NEW_PROFILE)

            # we might disconnect, so the fetching of the data can happen seperately
            # we can mark the data as ready to fetch for when we have recovered the float
            # does pushing a button on the keyboard count as autonomous?
            self.profile_ready = True

        else:
            # ask for data
            self.net.send(packets.RECEIVE_DATA_PLEASE)
            data = self.net.wait_for_packet(packets.DATA_PAYLOAD)
            self.consume_raw_data(data)

            # mark as ready for next profile
            self.profile_ready = False

        pass