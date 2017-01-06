import socket, atexit, os
import regraa_osc_tools as osc_tools

# dict mapping samplename to bufnum
samples = {}
sample_root = os.getenv("SAMPLE_ROOT", "/home/nik/SAMPLES")
bufnum = 0

port = 57110
address = "127.0.0.1"
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.setblocking(False)
sock.bind(("127.0.0.1", 54442))

def send(bundle):
    """Sends an OscBundle or OscMessage to the server."""
    sock.sendto(bundle.dgram, (address, port))

def register_sample(folder, name):
    global bufnum
    sample_id = folder + ":" + name
    if sample_id not in samples:
        sample_path = sample_root + "/" + folder + "/" + name + ".wav"
        # create buffer on scsynth
        send(osc_tools.build_message("/b_allocRead", bufnum, sample_path))
        samples[sample_id] = bufnum
        bufnum += 1

def free_samples():
    for sample in samples:
        send(osc_tools.build_message("/b_free", samples[sample]))

atexit.register(free_samples)

# init default group
send(osc_tools.build_message("/g_new", 1, 0, 0))
