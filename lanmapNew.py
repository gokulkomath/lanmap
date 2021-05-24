#! /usr/bin/python3

import socket
import subprocess
from sys import exit
import threading
from queue import Queue

alive_ip_list = []

q_for_alive = Queue()
q_for_ports = Queue()
thread_num = 100
port_range = 65535
lock = threading.Lock()


#fetching ip of this device-----------------------------------------------------------------------------------------------------------
def ip_fetch():
  
   try:
     
     result = subprocess.getoutput("ifconfig | grep broadcast | awk '{print $2}'")
   
     my_ip = result[0:result.find(".",-5)+1].strip()
     
     
     if my_ip == "":
       exit()

     else:
         
         return my_ip
         
   
   except:
       print("Netword Error!")
       exit()

#----------------------------------------------------------------------------------------


# check the host---------------------------------------------
def alive_checker(target_ip):
     global alive_ip_list
     
     alive = subprocess.run(["ping","-c","1",target_ip],capture_output=True)

     if alive.returncode == 0:
       with lock:
           alive_ip_list.append(target_ip)

#-----------------------------------------------------------------------------------

#Alive code starts here--------------------------------------------------------------------------------
def alive_checker_threader():
    while True:
        target_ip = q_for_alive.get()
        alive_checker(target_ip)
        q_for_alive.task_done()


#-portscanner-------------------------------------------------
def portscanner(target_ip,port,index):
    try:
       with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
           sock.settimeout(0.5)
           sock.connect((target_ip,port))

           with lock: 
              open_port_list[index].append(port)
              
              all_closed = True
    except:
        pass    
#---------------------klfdslakdsfldkffk----------------------------------------



def portscanner_threader(target_ip,index):
       while not q_for_ports.empty():
           p = q_for_ports.get()
           portscanner(target_ip, p,index)
           
           q_for_ports.task_done()


def display_result():
    for a in range(len(alive_ip_list)):
        print("\n")
        print(f"IP : {alive_ip_list[a]}")

        if len(open_port_list[a]) == 0:
            print("No Open Ports Available")
            continue

        for b in open_port_list[a]:
                print(f"Open Port : {b}")
            
                       

#-----------------ALL FUNCTIONS ARE DEFINED-------------------------------------------------------------------

my_ip = ip_fetch()

for x in range(1,256):
    q_for_alive.put(f"{my_ip}{x}")



for x in range(thread_num):
    thread = threading.Thread(target=alive_checker_threader)
    thread.daemon = True
    thread.start()

# clearing all alive threads and queues 

q_for_alive.join()
# Alive code ends here--------------------------------------------------------------------------------------------

#creating a nested list to hold open ports
open_port_list = [ [] for x in range(len(alive_ip_list)) ]
threadzz = []

for index in range(len(alive_ip_list)):

    for x in range(port_range):
        q_for_ports.put(x)
    
    
    
    for thread in range(thread_num):
        
        thread = threading.Thread(target=portscanner_threader,args=(alive_ip_list[index],index))
        threadzz.append(thread)
        thread.start()
       
    q_for_ports.join()
    
    #all threads for the ip is ended
    for x in threadzz:
        x.join()  
        
#result is displayed
display_result()
  
