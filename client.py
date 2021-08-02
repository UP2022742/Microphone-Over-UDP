from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

frames = []

def udpStream():
    udp = socket(AF_INET, SOCK_DGRAM)    

    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), ("127.0.0.1", 12345))

    udp.close()

def record(stream, CHUNK):    
    while True:
        frames.append(stream.read(CHUNK))

class SendData:
    def __init__(self) -> None:
        self.CHUNK = 1024
        self.FORMAT = paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.p = PyAudio()

        self.stream = self.p.open(
            format = self.FORMAT,
            channels = self.CHANNELS,
            rate = self.RATE,
            input = True,
            frames_per_buffer = self.CHUNK,
        )
        
    def main(self):
        
        Tr = Thread(target = record, args = (self.stream, self.CHUNK,))
        Ts = Thread(target = udpStream)
        
        Tr.setDaemon(True)
        Ts.setDaemon(True)
        
        Tr.start()
        Ts.start()
        
        Tr.join()
        Ts.join()

if __name__ == "__main__":
    SendData().main()