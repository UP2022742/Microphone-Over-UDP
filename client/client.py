from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import yaml

frames = []

class ConnectStream:
    def __init__(self, ip_address, port) -> None:
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self._running = True

        self.ip_address = ip_address
        self.port = port

    def stop(self):
        self._running = False

    def start(self):
        print("Sending socket data...")
        while self._running:
            if len(frames) > 0:
                self.socket.sendto(frames.pop(0), (self.ip_address, self.port))

        print("Closing socket...")
        self.socket.close()

class SendData:
    def __init__(self, ip_address: str, port: int) -> None:
        self.CHUNK = 8192
        self.FORMAT = paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.ip_address = ip_address
        self.port = port

        self.p = PyAudio()

        self.stream = self.p.open(
            format = self.FORMAT,
            channels = self.CHANNELS,
            rate = self.RATE,
            input = True,
            frames_per_buffer = self.CHUNK,
        )

        self.connect_stream = ConnectStream(ip_address, port)
        self.Tr = Thread(target = self.connect_stream.start, args = ())
        
    def main(self):
        
        if not self.ip_address or not self.port:
            print("Make sure that the IP and Port are defined")
            return

        try:
            print("Appending stream to frames...")
            self.Tr.start()
            while self.Tr.is_alive():
                frames.append(self.stream.read(self.CHUNK))

        except KeyboardInterrupt:
            self.connect_stream.stop()
            self.Tr.join()
        return 0

if __name__ == "__main__":
    ip_address = None
    port = None

    print("Reading configuration file...")
    with open('config.yml', 'r') as file:
        configuration_file = yaml.safe_load(file)
        
        # Define the IP and Port
        if not 'network' in configuration_file:
            print("Please make sure that the network header exists in the configuration file")
            exit(-1)
        
        if not 'public_ip_address' in configuration_file['network']:
            print("Make sure that 'public_ip_address' exists inside the network header")
            exit(-1)

        if not 'port' in configuration_file['network']:
            print("Make sure 'port' exists inside of the network header")
            exit(-1)

        ip_address = configuration_file['network']['public_ip_address']
        port = configuration_file['network']['port']
    
    print("Starting application...")
    SendData(ip_address, port).main()