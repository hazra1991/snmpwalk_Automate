#!/usr/bin/env python

from threading import Thread, Lock
import os,json,sys
thread_count = 500
success_file = 'success_file.txt'
no_snmp_access_file = "no_snmp_access.txt"
thread_lock = Lock()

with open (no_snmp_access_file,'w') as tp:
    pass
with open (success_file,'w') as tp:
    pass

with open ("PID_FILE.pid",'w') as pd:
    pd.write(str(os.getpid()))

def check_ip(ip):
    try:
        ip_list = ip.strip().strip("\n").split(".")
        if len(ip_list) == 4 :
            for i in ip_list:
                if " " in i or int(i)>255 or int(i) < 0 or '+' in i:
                    raise ValueError
            return True
    except ValueError:
        return False



def thread_fun(ip,cm_string):
    #TODO create a file for community strig

    for i in cm_string:
        snmp_cmd = "snmpwalk -v2c -c {} {} sysName".format(i, ip.strip('\n'))
        y = os.system(snmp_cmd)
        if y == 0:
            thread_lock.acquire()
            with open(success_file, "a+") as fd:
                fd.write("SNMP ACCESS ::- {}COMMUNITY STRING ::- {}\n===========\n".format(ip, i))
                thread_lock.release()
                return

    ping_cmd = "ping -W 2 -c 2 " + ip.strip('\n')
    x = os.system(ping_cmd)

    thread_lock.acquire()
    if x == 0:
        with open(no_snmp_access_file,"a+") as fd:
            fd.write("ONLY PING::- {}".format(ip))
    else:
        with open(no_snmp_access_file,"a+") as fd:
            fd.write("HOST UNREACHABLE::- {}".format(ip))
    thread_lock.release()


def main(ip_file_name=None,community_list=()):
    import time
    print("---->> LOADING IP FILE")
    time.sleep(2)
    try:
        with open(ip_file_name,"r") as fd:
            fp = open("invalid_ip_found.txt", "w")
            thread_pool = []
            for i in fd:
                if i != "\n" and check_ip(i):
                    th = Thread(target=thread_fun, args=(i,community_list))
                    th.start()
                    thread_pool.append(th)
                    if len(thread_pool) == thread_count:
                        for thr in thread_pool[::-1]:
                            thr.join()
                            thread_pool.pop()
                elif i == "\n":
                    continue
                else:
                    fp.write("invalid ip found -> {}\n".format(i.strip("\n")))
                    pass
            fp.close()
    except IOError:
        print("""
                [+]INPUT IP FILE NOT FOUND ---\n\n---> Create a filename 'ip_file.txt' in dir '{}/' and 
                place the ip-address to be checked ( "one ip on each line" )
                """.format(os.path.dirname(os.path.abspath(__file__))))
        return
    except KeyboardInterrupt:
        print("[+]-------program terminated manually")
        exit(0)

if __name__== "__main__":
    version = sys.version_info[0:2]
    try:
        if len(sys.argv) == 2 and int(sys.argv[1]) > 0:
            thread_count = int(sys.argv[1])
        elif len(sys.argv) != 1:
            raise ValueError
        
    except ValueError:
        print("[[FATAL ERROR]] Enter a proper numeric positive value for thread count\n\n--> CAUTION entering " +
              "inappropriate values can cause the program to crash.\n--> Default thread limit is %d" % thread_count)
        exit(0)
    print("\n{}Starting with {} thread workers{}\n".format(15 * '*', thread_count, 15 * '*'))
    print("---->> STARTING SEARCH \n---->> LOADING COMMUNITY STRINGS\n")
    try:
        cs = tuple(json.load(open("community_string.json",'r'))["community_string"])
        main("ip_file.txt",cs)
    except IOError:
        if version < (3,):
            data = raw_input("Community file not there,Do you want to proceed with just ping check?(y/n) :- ").lower()
            if data == 'y':
                main("ip_file.txt")
            else:
                print("""Create the file %s/community_string.json in the below format\n 
                                {
                                  "community_string":"string1","string2","string3","string4"]
                                }""" % os.path.dirname(os.path.abspath(__file__)))
        else:
            data = input("Community file not there,Do you want to proceed with just ping check?(y/n) :- ").lower()
            if data == 'y':
                main("ip_file.txt")
            else:
                    print("""Create the file %s/community_string.json in the below format\n 
                                                {
                                                  "community_string":["mystring1","mystring2",",mystring3"]
                                                }""" % os.path.dirname(os.path.abspath(__file__)))


    except ValueError:
        print("""\n[+] Error in reading data from %s/community_string.json .
                    \nPlease update in the below format **NOTE: 'mystring1' should be updated with 
                     the original community string \n\n
                            {
                              "community_string":["mystring1","mystring2",",mystring3"]
                            }\n\nIf no string needed keep it blank like '[]'\n""" % os.path.dirname(os.path.abspath(__file__)))

    except KeyboardInterrupt:
        print("""Create the file %s/community_string.json in the below format\n 
                                        {
                                          "community_string":"string1","string2","string3","string4"]
                                        }""" % os.path.dirname(os.path.abspath(__file__)))

