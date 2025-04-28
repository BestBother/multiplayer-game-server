import struct


HOST = '0.0.0.0'
PORT = 8000

#player_id (I), x (f), y (f)
MSG_FMT = '!Iff'
MSG_SIZE = struct.calcsize(MSG_FMT)
