import sys
import time

import pynng


def usage():
    """
    print usage message and exit.

    """
    print("Usage: {} node0|node1 URL".format(sys.argv[0]))
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        usage()
    node = sys.argv[1]
    if node not in ("node0", "node1"):
        usage()
    addr = sys.argv[2]
    with pynng.Pair0(recv_timeout=100, send_timeout=100) as sock:
        if node == "node0":
            sock.listen(addr)
        else:
            sock.dial(addr)
        while True:
            try:
                msg = sock.recv()
                print("got message from", msg.decode())
            except pynng.Timeout:
                pass
            time.sleep(0.5)
            try:
                sock.send(node.encode())
            except pynng.Timeout:
                pass


if __name__ == "__main__":
    main()