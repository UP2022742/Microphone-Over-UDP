from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import tkinter as tk

frames = []

def udpStream(stop, CHUNK, CHANNELS):

    udp = socket(AF_INET, SOCK_DGRAM)
    
    print("Binding to socket... 127.0.0.1:12345")
    udp.bind(("127.0.0.1", 12345))

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
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

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

        self.streams_active = False
        self.Ts = Thread(target = udpStream, args=(lambda : self.streams_active, self.CHUNK,self.CHANNELS))
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
    # RecvData().main()
    root = tk.Tk()
    root.geometry("150x100")

    app = Application(master=root)
    app.mainloop()