import socket, os, atexit
import subprocess 
import regraa_osc_tools as osc_tools

# dict mapping samplename to bufnum
akita_ports = {}
akita_sample_root = os.getenv("AKITA_SAMPLE_ROOT", "/home/nik/akita_samples")

address = "127.0.0.1"
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.setblocking(False)

akita_add_latency = 30

def quit_akita_instances():
    for instance in akita_ports:
        send(instance, osc_tools.build_message("/akita/quit"))
    
atexit.register(quit_akita_instances)

# hmrgl ... 
def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def load(*args, **kwargs):
    try:        
        send(args[0], osc_tools.build_message("/akita/quit"))
        print("replace " + args[0] + " at " + str(akita_ports[args[0]]))
    except KeyError:
        print("init " + args[0])        
    port = get_free_port();
    akita_ports[args[0]] = port
    add_params = "";
    for arg in kwargs:        
        add_params = add_params + "--" + arg.replace("_", "-") + "=" + str(kwargs[arg]) + " "
    cmd = "akita --interface OSC --udp-port {} {} {}.wav".format(port, add_params, akita_sample_root + "/" + args[1])
    subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        #stdout=subprocess.PIPE
    )

def send(instance, bundle):    
    """Sends an OscBundle or OscMessage to the server."""
    sock.sendto(bundle.dgram, (address, akita_ports[instance]))

