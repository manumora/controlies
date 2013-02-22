##############################################################################
# -*- coding: utf-8 -*-
# Project:     Controlaula
# Module:     NetworkUtils.py
# Purpose:     Several network utilities to be used in Python
# Language:    Python 2.5
# Date:        17-Jan-2010.
# Ver:        17-Jan-2010.
# Author:    José L. Redrejo Rodríguez
# Copyright:   2009 - José L. Redrejo Rodríguez    <jredrejo @nospam@ debian.org>
#
# ControlAula is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ControlAula is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ControlAula. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import array,fcntl,socket,struct,os,re
import logging,subprocess

gateway='0'
ltspGateway='0'
essid=''
bssid=''
IFNAMSIZE = 16
IW_ESSID_MAX_SIZE = 16
SIOCGIWESSID  = 0x8B1B
SIOCGIWAP     = 0x8B15

def get_ip_address(ifname):
    """Returns the ip address of the interface ifname"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip= socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15]) )[20:24]
            )
    except:
        ip=''
    return ip

def get_ip_inet_address(connection_ip='198.41.0.4'):
    """Returns the ip address of the interface used to connect to the given ip
    
    198.41.0.4 is a DNS ROOT Server, so it's the default value to connect to Internet
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    try: 
        s.connect((connection_ip, 0))
        inet_address= s.getsockname()[0]
    except:
        inet_address=''
    s.close()
    logging.getLogger().debug("Inet Address:" + inet_address)
    return inet_address 


def get_inet_HwAddr(connection_ip='192.168.0.254'):
    """Returns the mac address of the interface used to connect to the given ip"""
    interfaces=all_interfaces()
    rightIP=get_ip_inet_address(connection_ip)
    mac=''
    ifname=''
    for i in interfaces:
        if rightIP== get_ip_address(i[0]):
            ifname=i[0]
            break
    if ifname !='':
        mac=get_HwAddr(ifname)
        
    return mac
        


def get_HwAddr(ifname):
    """Returns the mac of the ifname network card"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    try:
        mac= ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
    except:
        mac=''
    
    return mac


def getWirelessNICnames():
    """ return list of  wireless device names   """
    device = re.compile('[a-z]{3,4}[0-9]') 
    ifnames = []
    
    f = open('/proc/net/wireless', 'r')
    data = f.readlines()
    for line in data:
        try:
            ifnames.append(device.search(line).group())
        except AttributeError:
            pass 
    
    return ifnames


def all_interfaces():
    """Returns all the available network interfaces in a linux machine"""
    max_possible = 128  # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl( s.fileno(), 0x8912,  struct.pack('iL', bytes, names.buffer_info()[0])    ))[0]
    namestr = names.tostring()
    #return [namestr[i:i+32].split('\0', 1)[0] for i in range(0, outbytes, 32)]
    lst = []
    arch64=(os.uname()[4]=='x86_64')
    if arch64:
        totalStruct=40
    else:
        totalStruct=32
    for i in range(0, outbytes, totalStruct):
        if arch64:
            name = namestr[i:i+16].split('\0', 1)[0]
        else:
            name = namestr[i:i+32].split('\0', 1)[0]
        ip   = namestr[i+20:i+24]
        lst.append((name, socket.inet_ntoa(ip)))


    return lst

def getESSID( ifname):

    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    essid = ""
    
    buff = array.array('c', '\0'*32)
    caddr_t, length = buff.buffer_info()
    s = struct.pack('Pi', caddr_t, length)
       
    buff2 = IFNAMSIZE-len(ifname)
    ifreq = ifname + '\0'*buff2
    ifreq = ifreq + s                  
    try:
        result = fcntl.ioctl(sockfd.fileno(), SIOCGIWESSID, ifreq)
        i=0
        result=result[16:]
    except IOError, (i, e):
        i=i
        result=e
            
    if i > 0:
        return (i, result)
    str = buff.tostring()
    return (0,str.strip('\x00'))


def getHostName():
    return socket.gethostname()

def getFreeTCPPort():
    """Returns a random free port provided by the Operative System"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 0))
    newPort= sock.getsockname()[1]
    sock.close()
    return newPort


def getWirelessData():
    global essid
    global bssid
    wifiNICs=getWirelessNICnames()
    if len(wifiNICs)>0:
        for i in wifiNICs:
            value,nessid=getESSID(i)
            if value==0:
                essid=nessid
                value2,nbssid=getAPaddr(i)
                if value2==0:
                    bssid=nbssid    

def getAPaddr(ifname):
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    buff = array.array('c', '\0'*32)
    caddr_t, length = buff.buffer_info()
    s = struct.pack('Pi', caddr_t, length)
        

    buff2 = IFNAMSIZE-len(ifname)
    ifreq = ifname + '\0'*buff2
    ifreq = ifreq + s                  
    try:
        result = fcntl.ioctl(sockfd.fileno(), SIOCGIWAP, ifreq)
        i=0
        result=result[16:]
    except IOError, (i, e):
        i=i
        result=e
                                  
                                  
    if i > 0:
        return (i, result)
    else:
        mac_addr = struct.unpack('xxBBBBBB',result[:8])
        return (0,"%02X:%02X:%02X:%02X:%02X:%02X" % mac_addr)
    
def scan_server(address, port): 
    """Returns true if a port is open at address, or false otherwise"""
    s = socket.socket() 
    #print "Attempting to connect to %s on port %s." %(address, port) 
    try: 
        s.connect((address, port)) 
        #print "Connected to server %s on port %s." %(address, port) 
        s.close()
        return True 
    except socket.error, e: 
        logging.getLogger().debug("Connecting to %s on port %s failed with the following error: %s" %(address, port, e))
        return False


def getUsableTCPPort(address,port):
    """Returns the first free port between port and port +10"""
    freeport=port
    for x in range(port,port+10): 
        check = scan_server(address, x) 
        if check==False :
            freeport=x
            break
    
    
    return freeport


def startup(address):

    addr_byte = address.split(':')
    hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
      int(addr_byte[1], 16),
      int(addr_byte[2], 16),
      int(addr_byte[3], 16),
      int(addr_byte[4], 16),
      int(addr_byte[5], 16))

    msg = '\xff' * 6 + hw_addr * 16
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.sendto(msg, ('<broadcast>', 9))
        s.sendto(msg, ('<broadcast>', 7))
        s.sendto(msg, ('192.168.0.255', 9))
        s.sendto(msg, ('192.168.0.255', 7))   
    except:
        s.sendto(msg, ('<broadcast>', 2000))
        s.sendto(msg, ('192.168.0.255', 2000))
    s.close()

def defaultGW():
    global gateway
    if gateway=='0':
        try:
            s=subprocess.Popen('/sbin/route -n|grep "0.0.0.0"|grep UG',shell=True,stdout=subprocess.PIPE).communicate()[0]
            gateway=s.splitlines()[0].split()[1]
        except:
            gateway='0'
    return gateway
    
def ltspGW():
    global ltspGateway
    if ltspGateway=='0':
        try:
            externalIP=get_ip_inet_address()
            internalIP=get_ip_inet_address('192.168.0.2')
        
            if externalIP==internalIP or externalIP=='':
                ltspGateway=defaultGW()
            else:
                ltspGateway=internalIP
        except:
            ltspGateway='0'
    return ltspGateway

def cleanRoutes():
    s=subprocess.Popen(['route','-n'],stdout=subprocess.PIPE).communicate()[0]
    l=s.splitlines()
    for route in l:
        target=route.split()[0]
        if target[:4]=='239.':
            subprocess.Popen(['route','del','-net',target + '/24'])
            
def addRoute(net,gw=''):
    if gw=='':
        newgw=defaultGW()
    else:
        newgw=gw
    subprocess.Popen(['route','add','-net',net+ '/24','gw',newgw])
