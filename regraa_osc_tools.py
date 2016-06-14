from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder

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
