from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import tkinter as tk
import yaml

frames = []

def udpStream(stop, port, CHUNK, CHANNELS):

    udp = socket(AF_INET, SOCK_DGRAM)
    
    print("Binding to socket... 127.0.0.1:12345")
    udp.bind(("0.0.0.0", port))

    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)

        if stop():
            break

    udp.close()

def play(stop, stream, CHUNK):
    BUFFER = 10
    while True:
        if len(frames) == BUFFER:
            while True:
                try:
                    stream.write(frames.pop(0), CHUNK)
                except IndexError:
                    break
                if stop():
                    break

class Application(tk.Frame):
    def __init__(self, port, master=None):
        super().__init__(master)
        self.master = master

        if not port:
            print("Make sure that the port is defined in the configuration file")
            return

        self.port = port

        self.pack()
        self.create_widgets()

        self.FORMAT = paInt16
        self.CHUNK = 8192
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

        self.streams_active = False
        self.Ts = Thread(target = udpStream, args=(lambda : self.streams_active, self.port, self.CHUNK,self.CHANNELS))
        self.Tp = Thread(target = play, args=(lambda : self.streams_active, self.stream, self.CHUNK,))

    def toggle_stream(self):
        if self.streams_active:
            
            self.Ts.join()
            self.Tp.join()
        else:
            self.Ts.daemon = True
            self.Tp.daemon = True

            self.Ts.start()
            self.Tp.start()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Toggle Stream"
        self.hi_there["command"] = self.toggle_stream
        self.hi_there.pack(side="top")

if __name__ == "__main__":
    port = None

    print("Reading configuration file...")
    with open('config.yml', 'r') as file:
        configuration_file = yaml.safe_load(file)

        if not 'network' in configuration_file:
            print("Please make sure that the network header exists in the configuration file")
            exit(-1)

        if not 'port' in configuration_file['network']:
            print("Make sure 'port' exists inside of the network header")
            exit(-1)

        port = configuration_file['network']['port']

    root = tk.Tk()
    root.geometry("150x100")

    app = Application(port=port, master=root)
    app.mainloop()