import os
import signal
import subprocess
import time

def record_bluetooth_input(file_path):
    maybe_index_is_in_here = [s for s in str(subprocess.run('pacmd list-sources', stdout=subprocess.PIPE, shell=True).stdout).split(' ') if "name" in s]
    device_num = maybe_index_is_in_here[-2][:maybe_index_is_in_here[-2].find('\\n')]
    rate = 16000

    print("device num: ", device_num)

    cmd = "parec -r --rate=" + str(rate) + " --device=" + device_num + " --file-format=wav > " + file_path

    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           shell=True, preexec_fn=os.setsid)

    time.sleep(2)

    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
