from read_ini_file import *
from CAN import *
import time
import struct
import os
ch1 = 0
ch2 = 0
kvaser_open = 1
file_name_temp = []
state = 0
f = None


def record_file_name(msg):
    ch = []
    for i in msg:
        if i == 0:
            ch.append()
            return ''.join(ch)
        else:
            ch.append(chr(i))
    return ''.join(ch)


def read_id(msg):
    global state 
    if msg[0] == int(nameID, 16):
        state = 1
        return record_file_name(msg[-1])
    else:
        state = 0
        return False


def fsm_step(msg):
    '''
    state machine:
        0: jugement ID. When id = 0x100, trigger 1 state
        1: record file name and crate file. When id = 0x200, trigger 2 state
        2: write data and close file. when id = 0x100, trigger 1 state
    '''

    global state
    global file_name_temp
    global f, t
    if state == 0:
        num = read_id(msg)
        if num:
            file_name_temp += num
        return True

    if state == 1:
        if file_name_temp[-1] == ' ':
            file_name_temp = ''.join(file_name_temp)
            path = os.path.join(home_path, file_name_temp)
            try:
                f =  open(path, "wb+")
            except Exception as e:
                 print('error: No directory{0}'.format(e))
            file_name_temp = []
            state = 2
            return True
        else:
            num = record_file_name(msg[-1])
            file_name_temp += num
            return True

    if state == 2:
        if msg[0] == int(dataID, 16):
            t = time.time()
            for i in msg[-1]:
                f.write(struct.pack('B', i))
            return True
            
        if msg[0] == int(nameID, 16):
            f.close()
            num = record_file_name(msg[-1])
            file_name_temp += num
            state = 1
            return True
        
        if time.time() - t > 10:
            f.close()
            return True
           


def record_file_name(msg):
    ch = []
    for i in msg:
        if i == 0:
            ch.append(' ')
            return ''.join(ch)
        else:
            ch.append(chr(i))
    return ''.join(ch)



clear_buffer(kvaser_open, ch1, ch2)
open_can(kvaser_open, ch1, ch2)

while True:
    
    msg_collect = receive_can(kvaser_open, ch1, ch2)
    for msg_solo in msg_collect:
        if isinstance(msg_solo, list) and msg_solo !=[]:
            if msg_solo[0]!= int(nameID, 16) and msg_solo[0]!= int(dataID, 16):
                continue
            else:  
                fsm_step(msg_solo[0:-1])
                print(msg_solo[0:-1])


        