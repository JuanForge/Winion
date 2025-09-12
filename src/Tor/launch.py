import subprocess
import win32job
import win32con
import win32api
import atexit
import time
import os

def launch():
    job = win32job.CreateJobObject(None, "")
    extended_info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    extended_info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, extended_info)
    
    with open("Bin\\Tor\\Conf", 'w', encoding='utf-8') as file:
        file.write("""
SocksPort 127.0.0.1:9050

Log notice file logfile.txt

DataDirectory tor_data
GeoIPFile data/geoip
GeoIPv6File data/geoip6
                    """)
    proc = subprocess.Popen(["Bin\\Tor\\tor\\tor.exe", "-f", "Conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.join(os.getcwd(), "Bin", "Tor"))
    
    hProcess = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, proc.pid)
    win32job.AssignProcessToJobObject(job, hProcess)
    return proc, job

# time.sleep(120)
# # Nettoyage
# atexit.register(proc.terminate)
# atexit.register(lambda: win32job.CloseHandle(job))
# 