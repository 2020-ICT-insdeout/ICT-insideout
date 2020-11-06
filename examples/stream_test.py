import os
import signal
import subprocess
import time
import sys


maybe_index_is_in_here = [s for s in str(subprocess.run('pacmd list-sources', stdout=subprocess.PIPE, shell=True).stdout).split(' ') if "name" in s]
device_num = maybe_index_is_in_here[-2][:maybe_index_is_in_here[-2].find('\\n')]
rate = 16000

cmd = "parec -r --rate=" + str(rate) + " --device=" + device_num + " --channels=1"

# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                       shell=True, preexec_fn=os.setsid)

iterate_num = 5

header_size = 44
duration_sec = 3
duration_byte = rate * 2 * duration_sec + header_size

temp = '{:08x}'.format(duration_byte - 8, 'x')
litte_endian_chunk_size1 = "{}{}{}{}".format(temp[6:], temp[4:6], temp[2:4], temp[:2])
temp = '{:08x}'.format(duration_byte - header_size, 'x')
litte_endian_chunk_size2 = "{}{}{}{}".format(temp[6:], temp[4:6], temp[2:4], temp[:2])

header = bytes.fromhex('52494646' + litte_endian_chunk_size1 + '57415645666d74201000000001000100803e0000007d00000200100064617461' + litte_endian_chunk_size2)

a = header
b = []
i = 0
for line in iter(process.stdout.readline, 'b'):
    a += line
    if len(a) > duration_byte:
        print(i)
        b.append(a[:duration_byte])
        a = header + a[duration_byte:]
        i += 1
        if i >= iterate_num:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send the signal to all the process groups
            break

for i, wav in enumerate(b):
    file_name = 'test/test_' + str(i)
    with open(file_name + '.wav', 'wb') as file:
        file.write(wav)