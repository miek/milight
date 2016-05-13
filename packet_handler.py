from bitstring import *
import crcmod
import pmt
import zmq

button_mask = 0b1111
long_press_mask = 0b10000

button_map = {
    2:  "#4 on",
    3:  "#2 off",
    4:  "Decrease brightness",
    5:  "All on",
    6:  "#4 off",
    7:  "#3 on",
    8:  "#1 on",
    9:  "All off",
    10: "#3 off",
    11: "#1 off",
    12: "Increase brightness",
    13: "#2 on",
    14: "Decrease colour temp.",
    15: "Increase Colour temp.",
}

def bitstring_to_bytes(pkt):
    ret = []
    for i in range(0, len(pkt), 8):
        # get 8 bits
        chunk = pkt[i:i+8]

        # reverse bit order
        chunk = chunk[::-1]

        # bitstring -> int -> byte
        ret.append(chr(int(chunk, 2)))
    return ''.join(ret)

def crc_check(pkt):
    pkt_bytes = bitstring_to_bytes(pkt)
    crc_func = crcmod.predefined.mkPredefinedCrcFun('kermit')
    return crc_func(pkt_bytes) == 0


def slice_int(str, count, reverse = True):
    s1,s2 = slice_str(str, count, reverse)
    return int(s1, 2), s2

def slice_str(str, count, reverse = True):
    s1,s2 = str[0:count], str[count:]
    if reverse:
        s1 = s1[::-1]
    return s1,s2

def handle_packet(pkt):
    length,    pkt = slice_int(pkt, 8)
    remote_id, pkt = slice_int(pkt, 24)
    group,     pkt = slice_int(pkt, 8)
    button,    pkt = slice_int(pkt, 8)
    count1,    pkt = slice_int(pkt, 8)
    count2,    pkt = slice_int(pkt, 8)
    crc,       pkt = slice_int(pkt, 16)

    long_press = bool(button & long_press_mask)
    button = button & button_mask

    print "len: {} remote_id: {} group: {} button: {} long press: {} counts: ({}, {}) crc: {}".format(
        length,
        hex(remote_id),
        group,
        button_map[button],
        long_press,
        count1,
        count2,
        hex(crc))

def main():
    context = zmq.Context()

    subscriber = context.socket(zmq.SUB)
    subscriber.connect('tcp://localhost:7182')
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    repeat_count = 0
    prev_packet = ""
    while True:
        msg = subscriber.recv()
        p = pmt.deserialize_str(msg)
        pkt = pmt.to_python(p)[1]

        if crc_check(pkt) and prev_packet != pkt:
            handle_packet(pkt)
        prev_packet = pkt

if __name__ == "__main__":
    main()