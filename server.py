from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

frames = []

def udpStream(CHUNK, CHANNELS):

    udp = socket(AF_INET, SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12345))

    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)

    udp.close()

def play(stream, CHUNK):
    BUFFER = 10
    while True:
        if len(frames) == BUFFER:
            while True:
                stream.write(frames.pop(0), CHUNK)

class RecvData:
    def __init__(self):
        self.FORMAT = paInt16
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.RATE = 44100

        self.p = PyAudio()

        self.stream = self.p.open(
            format=self.FORMAT,
            channels = self.CHANNELS,
            rate = self.RATE,
            output = True,
            frames_per_buffer = self.CHUNK,
        )

    def main(self):

        Ts = Thread(target = udpStream, args=(self.CHUNK,self.CHANNELS))
        Tp = Thread(target = play, args=(self.stream, self.CHUNK,))
       
        Ts.setDaemon(True)
        Tp.setDaemon(True)
       
        Ts.start()
        Tp.start()
      
        Ts.join()
        Tp.join()

if __name__ == "__main__":
    RecvData().main()