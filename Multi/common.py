# common.py
import struct

# network settings
HOST = '172.20.209.22'
PORT = 5000

# simple struct: player_id (I), x (f), y (f)
MSG_FMT = '!Iff'
MSG_SIZE = struct.calcsize(MSG_FMT)
