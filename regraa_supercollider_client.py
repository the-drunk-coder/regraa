import socket, atexit, os
from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder

# dict mapping samplename to bufnum
samples = {}
sample_root = os.getenv("SAMPLE_ROOT", "~/samples")
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
        send(build_message("/b_allocRead", bufnum, sample_path))
        samples[sample_id] = bufnum
        bufnum += 1

def free_samples():
    for sample in samples:
        send(build_message("/b_free", samples[sample]))

atexit.register(free_samples)

def build_message(*args):
    """Sends an OscBundle or OscMessage to the server."""
    msg = osc_message_builder.OscMessageBuilder(address = args[0])
    for arg in args[1:]:
        msg.add_arg(arg)
    return msg.build()

def build_bundle(timestamp, content):
    """Sends an OscBundle or OscMessage to the server."""
    bundle = osc_bundle_builder.OscBundleBuilder(timestamp)
    bundle.add_content(content)        
    return bundle.build()

# init default group
send(build_message("/g_new", 1, 0, 0))
