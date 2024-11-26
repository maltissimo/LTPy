import paramiko
import time
def measure_ssh_time(host,username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname = host, username = username, password = password)
        start_time = time.time()

        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()
        end_time = time.time()

        trip_time = (end_time - start_time )* 1000

        print(f"ROundtrip time: {trip_time:.2f} ms" )
    finally:
        client.close()
    return(trip_time)

host = "192.168.0.200"
username = "root"
password = "deltatau"
command = "echo Hello"
cum_time = 0
for i in range (100):
    time1 = measure_ssh_time(host,username, password, command)
    cum_time = cum_time + time1
    i = i+1
average = cum_time /100
print(f"Average time: {average:.2f} ms")