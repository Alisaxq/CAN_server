from optparse import OptionParser
import kvaser
from ctypes import *
import ctypes
from read_ini_file import *

VCI_USBCAN2A = 4
STATUS_OK = 1
set_baudrate = [[[500], [0x00, 0x1C]],[[1000], [0x00, 0x14]]]


# define struct of int_can
class VCI_INIT_CONFIG(Structure):  
    _fields_ = [("AccCode", c_ulong),
                ("AccMask", c_ulong),
                ("Reserved", c_ulong),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]
    
# define struct of can_data
class VCI_CAN_OBJ(Structure):   
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte * 8),
                ("Reserved", c_ubyte * 3)
                ]

vco = []
for i in range(2500):
    name = 'can_msg_'+str(i)
    tup = (name,VCI_CAN_OBJ)
    vco.append(tup)
class CAN_OBJ(Structure):  # 定义最大存放2500条CAN消息的CAN数据结构体
    _fields_ = vco

# D:\XIAO QI\Can\Can_server
canDLL = windll.LoadLibrary('D:/XIAO QI/Can/Can_server/ControlCAN.dll')

if int(baudrate) == 500 or int(baudrate) == 1000:
    for i in range(0, len(set_baudrate)):
        if set_baudrate[i][0][0] == int(baudrate):
            vci_initconfig = VCI_INIT_CONFIG(0x80000008, 0xFFFFFFFF, 0, 2, set_baudrate[i][1][0], set_baudrate[i][1][1], 0)
else:
    raise ValueError('baudrate is error')


def open_can(kva,ch1,ch2):
    if kva == 1:
        k = kvaser.open_can()
        if k != 1:
            return 0
        else:
            return 1
    if ch1 == 1:
        ret = canDLL.VCI_OpenDevice(VCI_USBCAN2A, 0, 0)
        ret = canDLL.VCI_InitCAN(VCI_USBCAN2A, 0, 0, byref(vci_initconfig))  #初始化通道0
        canDLL.VCI_StartCAN(VCI_USBCAN2A, 0, 0)                        #start_CAN
        if ret != STATUS_OK:
            return 0
        else:
            return 1
    if ch2 == 1:
        ret = canDLL.VCI_OpenDevice(VCI_USBCAN2A, 0, 0)
        ret = canDLL.VCI_InitCAN(VCI_USBCAN2A, 0, 1, byref(vci_initconfig))  #初始化通道1
        canDLL.VCI_StartCAN(VCI_USBCAN2A, 0, 1)  # start_CAN
        if ret != STATUS_OK:
            return 0
        else:
            return 1

def close_can(kva,ch1,ch2):   #关闭CAN
    if kva == 1:
        kvaser.close_can()
    if ch1 == 1:
        canDLL.VCI_CloseDevice(VCI_USBCAN2A, 0)
    if ch2 == 1:
        canDLL.VCI_CloseDevice(VCI_USBCAN2A, 1)


def receive_can(kva,ch1,ch2):  #CAN接收
    if kva == 1:
        try:
            can_data = kvaser.receive_can()
            return [can_data]
        except:
            return 0
    else:
        # CAN分析仪接收数据
        ubyte_array = c_ubyte * 8
        a = ubyte_array(1, 2, 3, 4, 5, 6, 7, 64)
        ubyte_3array = c_ubyte * 3
        b = ubyte_3array(0, 0, 0)
        vci_can_obj = CAN_OBJ()

        if ch1 == 1:
            # ret1 = canDLL.VCI_Receive(VCI_USBCAN2A, 0, 0, byref(vci_can_obj), 1, 0)
            
            ret1 = canDLL.VCI_Receive(VCI_USBCAN2A, 0, 0, ctypes.addressof(vci_can_obj), 2500, 0)
            if ret1 <= 0:
                return 0
            else:
                msg_list = []
                for i in range(ret1):
                    num = 'can_msg_' + str(i)
                    ID = eval('vci_can_obj.' + num + '.ID')
                    DATA = eval('vci_can_obj.' + num + '.Data')
                    can_data = [ID, list(DATA)]
                    msg_list.append(can_data)
      
                return msg_list
        if ch2 == 1:
            # ret2 = canDLL.VCI_Receive(VCI_USBCAN2A, 0, 1, byref(vci_can_obj), 1, 0)
            ret2 = canDLL.VCI_Receive(VCI_USBCAN2A, 0, 1,  ctypes.addressof(vci_can_obj), 2500, 0)
            if ret2 <= 0:
                return 0
            else:
                msg_list = []
                for i in range(ret2):
                    num = 'can_msg_' + str(i)
                    ID = eval('vci_can_obj.' + num + '.ID')
                    DATA = eval('vci_can_obj.' + num + '.Data')
                    can_data = [ID, list(DATA)]
                    msg_list.append(can_data)
                return msg_list
            

def send_can(can_id,can_data,kva,ch1,ch2):
    if kva == 1:
        send = kvaser.send_can(can_id, can_data)
        if send != 0:
            return 1
        else:
            return 0
    else:
        ubyte_array = c_ubyte * 8
        a = ubyte_array(can_data[0],can_data[1],can_data[2],can_data[3],can_data[4],can_data[5],can_data[6],can_data[7])
        ubyte_3array = c_ubyte * 3
        b = ubyte_3array(0, 0, 0)
        vci_can_obj = VCI_CAN_OBJ(can_id, 0, 0, 0, 0, 0, 8, a, b)

        if ch1 == 1:
            ret1 = canDLL.VCI_Transmit(VCI_USBCAN2A, 0, 0, byref(vci_can_obj), 1)
            if ret1 != STATUS_OK:
                return 0
            else:
                return [can_id, can_data, vci_can_obj.TimeStamp]
        if ch2 == 1:
            ret2 = canDLL.VCI_Transmit(VCI_USBCAN2A, 0, 1, byref(vci_can_obj), 1)
            if ret2 != STATUS_OK:
                return 0
            else:
                return [can_id, can_data, vci_can_obj.TimeStamp]

def clear_buffer(kva,ch1,ch2):
    if kva == 1:
        pass
    if ch1 == 1:
        canDLL.VCI_ClearBuffer(VCI_USBCAN2A, 0, 0)
    if ch2 == 1:
        canDLL.VCI_ClearBuffer(VCI_USBCAN2A, 0, 1)
    
