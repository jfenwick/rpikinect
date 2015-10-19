import OSC
import socket

def get_ip():
    ip = ''
    try:
        sock.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
        ip = sock.getsockname()[0]
    except socket.error as e:
        print "socket.error({0}): {1}".format(e.errno, e.strerror)
    return ip

def depth_handler(addr, tags, data, source):
    print "Got an update"
    print data
    #current_depth = int(data)

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = ''
    ip = get_ip()
    while ip == '':
        ip = get_ip()

    server =  OSC.OSCServer((ip,7400))
    server.addMsgHandler("/depth", depth_handler)
    server.serve_forever()