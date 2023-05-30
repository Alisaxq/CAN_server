from optparse import OptionParser
import configparser

# Read configuration
parser = OptionParser()
parser.add_option("-d", "--device", dest = "DeviceName", help = 'device used')
parser.add_option("-b", "--baud_rate", dest = "BaudRate", help = 'baud Rate')
parser.add_option("-n", "--nameid", dest = "NameID", help = 'flag for creat file')
parser.add_option("-a", "--dataid", dest = "DataID", help = "flag of write data")
parser.add_option("-f", "--folding_path", dest = 'HomePath', help = 'home path')
(options, args) = parser.parse_args()


try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if (not options.DeviceName):
        device = config.get('CAN', 'Device')
    else:
        device = options.DeviceName
    if (not options.BaudRate):
        baudrate = config.get('CAN', 'Baudrate')
    else:
        baudrate = options.BaudRate
    if (not options.NameID):
        nameID = config.get('CAN', 'Name ID')
    else:
        nameID = options.NameID
    if (not options.DataID):
        dataID = config.get('CAN', 'Data ID')
    else:
        dataID = options.DataID
    if (not options.HomePath):
        home_path = config.get('HOME', 'Path')
    else:
        home_path = options.HomePath
except Exception as e:
    print('error: configparser error{0}'.format(e))


        
