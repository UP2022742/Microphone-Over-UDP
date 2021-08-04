from pyaudio import PyAudio, paInt16
from socket import socket, AF_INET, SOCK_DGRAM, error as socketerr
from threading import Thread
from yaml import safe_load as yaml_safe_load
from os import path

frames = []

class BindStream:
    def __init__(self, port, chunk, channels) -> None:
        self.client_ips = self.get_saved_ips()

        self.socket = socket(AF_INET, SOCK_DGRAM)

        self.port = port
        self.chunk = chunk
        self.channels = channels

        self._running = True

    def get_saved_ips(self):
        if path.exists('clients.lst'):
            with open('clients.lst', 'r') as clients:
                return [client.strip() for client in clients]
        else:
            return []

    def stop(self):
        self._running = False

    def start(self):
        try:
            self.socket.bind(("0.0.0.0", self.port))
        except socketerr as e:
            print(str(e))

        while self._running:
            soundData, addr = self.socket.recvfrom(self.chunk * self.channels * 2)

            # If the file contains anything.
            if len(self.client_ips) > 0:
                if self.client_ips[-1] != addr[0]:
                    current_ip_address = addr[0]
                    
                    # If the address isn't in the known list.
                    if current_ip_address not in self.client_ips:
                        confirmation = input("Accept {} to list of knows IP's? (yes) ".format(current_ip_address))
                        if confirmation == "":

                            print("Adding {} to the list of known IP addresses...".format(current_ip_address))
                            with open('clients.lst', 'a+') as clients:
                                clients.write(current_ip_address+'\n'); 
                                self.client_ips.append(current_ip_address)
                        else:
                            break
            else:
                current_ip_address = addr[0]
                confirmation = input("Add {} to list of knows IP's? (yes) ".format(current_ip_address))
                if confirmation == "":

                    print("Adding {} to the list of known IP addresses...".format(current_ip_address))
                    with open('clients.lst', 'a+') as clients:
                        clients.write(current_ip_address+'\n'); 
                        self.client_ips.append(current_ip_address)
                else:
                    break

            frames.append(soundData)
        self.socket.close()
        print("Socket closed...")

class Application():
    def __init__(self, port):

        if not port:
            print("Make sure that the port is defined in the configuration file")
            return

        self.port = port
        self.format = paInt16
        self.chunk = 8192
        self.channels = 1
        self.rate = 44100

        self.buffer = 10

        self.p = PyAudio()

        self.stream = self.p.open(
            format=self.format,
            channels = self.channels,
            rate = self.rate,
            output = True,
            frames_per_buffer = self.chunk,
        )

        self.bind_stream = BindStream(self.port, self.chunk, self.channels)
        # self.play_sound = PlaySound(self.stream, self.chunk)

        self.Ts = Thread(target = self.bind_stream.start, args=())
        # self.Tp = Thread(target = self.play_sound.start, args=())

        self.Ts.daemon = True
        # self.Tp.daemon = True

        self.main()

    def main(self):
        try:
            print("Listening to streams...")
            self.Ts.start()
            while True:
                if len(frames)==self.buffer:
                    while self.Ts.is_alive():
                        try:
                            self.stream.write(frames.pop(0), self.chunk)
                        except IndexError:
                            break
        except KeyboardInterrupt:
            self.bind_stream.stop()
            self.Ts.join()
        return 0

if __name__ == "__main__":
    port = None
    # signal.signal(signal.SIGINT, signal_handler)

    print("Reading configuration file...")
    with open('config.yml', 'r') as file:
        configuration_file = yaml_safe_load(file)

        if not 'network' in configuration_file:
            print("Please make sure that the network header exists in the configuration file")
            exit(-1)

        if not 'port' in configuration_file['network']:
            print("Make sure 'port' exists inside of the network header")
            exit(-1)

        port = configuration_file['network']['port']

    Application(port=port)


# TODO:
# IMPLEMENT BLOCKED IPS METHOD SO IT IGNORES THE IP IF IN THE LIST, SHOULDN'T
# BE HARD.
# Shove frames into class instead of global.
# Fix hanging on control + c when listening for a socket.