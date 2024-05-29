import serial
import time

def init_serial(port, baudrate):
    try:
        ser = serial.Serial(port,baudrate,
                            bytesize=serial.EIGHTBITS,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE,
                            timeout = 1,
                            xonxoff =  False,
                            rtscts = False,
                            dsrdtr = False,
                            inter_byte_timeout = None,
                            write_timeout = 2)
        if ser.is_open:
            print(f"serial port {port} is open")
        else:
            print(f"failed to open serial port {port}")
    except serial.SerialException as e:
                  print(f" error opening serial port {port}: {e}")
    return ser


def write_to_serial(ser, data):
    try:
        command = str(data) + "\r\n"
        ser.write(command.encode('ascii'))
        print(f" Data sent: {command}")
    except serial.SerialException as e:
        print(f"SerialException: Error writing to serial port: {e}")
    except Exception as e:
        print(f"Exception: an unexpected error occurred: {e}")


def read_from_serial(ser):
    try:
        time.sleep(1)
        response = ser.read_all().decode('ascii').strip()

        """
        start_time = time.time()
            while True: 
            if ser.in_waiting >0:
                chunk = ser.read(ser.in_waiting).decode('ascii')
                response += chunk
                if '\n' in responnse: 
                    break
            if time. time() - start_time > ser.timeout:
                print("Read timeout")
                break    
           """
        # response = ser.read_until(b'\n').decode('ascii').strip()
        if response:
            print(f"Response from USB device: {response}")
        else:
            print("No response received")
    except serial.SerialException as e:
        print(f"SerialException: Error reading from serial port: {e}")
    except Exception as e:
        print(f"Exception: an unexpected error occurred: {e}")


port = "/dev/ttyACM0"
baud = 9600
print("opening serial port... ")
ser = init_serial(port, baud)

if ser:
    if ser.is_open:
        data_to_send = "SOURce:AM:SOURce?"
        print(f"sending the {data_to_send} command...")
        write_to_serial(ser, data_to_send)

        time.sleep(0.1)

        print("Reading response... ")

        read_from_serial(ser)

        if ser.in_waiting > 0:
            print(f" still some data in the buffer: {ser.in_waiting} bytes")
        try:
            print("closing serial port... ")
            ser.close()
            print(f"Serial port {port} closed")
        except serial.SerialException as e:
            print(f"SerialException: Error closing serial port {e}")
        except Exception as e:
            print(f" Exception: An unexpected error occurred whiel closing: {e}")
    else:
        print(f"Serial port {port} is not open, cannot proceed")
else:
    print("Failed to initialize serial port, cannot proceed")