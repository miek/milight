from bitstring import *
import pmt
import zmq

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
    button,    pkt = slice_str(pkt, 8)
    count1,    pkt = slice_int(pkt, 8)
    count2,    pkt = slice_int(pkt, 8)
    crc,       pkt = slice_int(pkt, 16)
    print "len: {} remote_id: {} group: {} button: {} long press: {} counts: ({}, {}) crc: {}".format(
        length,
        hex(remote_id),
        group,
        button,
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

        # Very lazy integrity checking
        if pkt == prev_packet:
            if repeat_count == 4:
                handle_packet(pkt)
            repeat_count += 1
        else:
            repeat_count = 0
        prev_packet = pkt

if __name__ == "__main__":
    main()