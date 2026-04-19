import threading
import struct
from src.common import consts
from src.client.logger import Logger
from src.client.float import packets
from src.client.float.floatnetwork import FloatNetworker



class FloatInterface():
    """
    Interface to our float, Morag
    """

    def __init__(self, ) -> None:
        self.net = FloatNetworker()
        self.profile_ready = False

        self.profile: int = 0
        self.temperature: float = 0.0
        self.processed_data: list[tuple[float, float]] = []


    def run(self):
        Logger.log("attempting float process")
        process_thread = threading.Thread(target=self._run_thread_activity)
        process_thread.run()

    
    def consume_raw_data(self, data: bytes):
        offset = 0

        self.profile, self.temperature = struct.unpack_from(FloatNetworker.OTHER_DATA_FORMAT, data, offset)
        offset += struct.calcsize(FloatNetworker.OTHER_DATA_FORMAT)

        points = []
        count, = struct.unpack_from(">i", data, offset)
        offset += struct.calcsize(">i")

        for i in range(count):
            points.append(struct.unpack_from(FloatNetworker.POINT_FORMAT, data, offset + i * struct.calcsize(FloatNetworker.POINT_FORMAT)))
        
        self.processed_data = []
        for datum in points:
            self.processed_data.append(
                (datum[0], datum[1])
            )

    def get_processed_data(self) -> list[tuple[float, float]]:
        return self.processed_data


    def _run_thread_activity(self):
        
        if not self.profile_ready:

            # tell go down
            self.net.send(FloatNetworker.build_packet(packets.START_NEW_PROFILE))

            # we can mark the data as ready to fetch for when we have recovered the float

            data = self.net.wait_for_packet(packets.ACK)
            if data:
                self.profile_ready = True
                Logger.log("started float profile")
            else:
                Logger.log("failed to start profile (probably not connected)")

        else:
            # ask for data
            self.net.send(FloatNetworker.build_packet(packets.RECEIVE_DATA_PLEASE))
            
            data = self.net.wait_for_packet(packets.DATA_PAYLOAD)
            if data:
                self.consume_raw_data(data)

                # mark as ready for next profile
                self.profile_ready = False
                Logger.log("received float profile")
            else:
                Logger.log("failed to receive profile (probably not connected or not ready)")

        pass