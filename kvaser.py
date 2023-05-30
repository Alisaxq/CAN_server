import canlib.canlib as canlib

# cl = canlib.canlib()
# ch = cl.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)


def open_can():
    global c1
    global ch
    try:
        cl = canlib.canlib()
        ch = cl.openChannel(0, canlib.canOPEN_REQUIRE_EXTENDED)
        #   ch.setBusParams(canlib.canBITRATE_500K)
        ch.setBusParams(canlib.canBITRATE_1M)
        ch.busOn()
        return 1
    except:
        return 0

def send_can(can_id,can_data):
    try:
        ch.writeWait(can_id, can_data,0, timeout=50)
        return 1
    except:
        return 0

def dumpMessage(id, msg, dlc, flag, time):
    """Prints a message to screen"""
    if (flag & canlib.canMSG_ERROR_FRAME != 0):
        # print("***ERROR FRAME RECEIVED***")
        return 0
    else:
        return [id,list(msg)]



def receive_can():
    try:
        id, msg, dlc, flag, time = ch.read(50)
        if (flag & canlib.canMSG_ERROR_FRAME != 0):
            return 0
        else:
            return [id, list(msg),time]
    except(canlib.canNoMsg) as ex:
        return 0


def close_can():
    ch.busOff()
    ch.close()

