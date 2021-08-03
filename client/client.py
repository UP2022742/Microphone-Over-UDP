from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import yaml

frames = []

def udpStream(ip_address, port):
    udp = socket(AF_INET, SOCK_DGRAM)    
    print("Sending to socket...")
    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), (ip_address, port))

    udp.close()

def record(stream, CHUNK):
    print("Appending stream to frames...")
    while True:
        frames.append(stream.read(CHUNK))

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
        
    def main(self):
        
        if not self.ip_address or not self.port:
            print("Make sure that the IP and Port are defined")
            return

        print("Starting threads...")

        Tr = Thread(target = record, args = (self.stream, self.CHUNK,))
        Ts = Thread(target = udpStream, args=(self.ip_address, self.port,))
        
        Tr.daemon = True
        Ts.daemon = True
        
        Tr.start()
        Ts.start()
        
        Tr.join()
        Ts.join()

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