from firebase import Database
from stream import VideoStream
from system import System
import threading
import time
import serial
import typing

class Printer:
    
    def __init__(self, com_port: str, database: Database):

        # Runtime variables
        self.status: str = 'idle'
        
        # Set up firebase 
        self.__database = database
        self.__watch = self.__database.set_up_database_watch(self.__on_snapshot_callback)
        
        # Start Printer Up
        baudrate = self.__database.read('baudrate')
        self.__printer_serial = Printer.__open_serial(com_port, baudrate)

        if self.__printer_serial != None:
            self.__ok_msg = self.__identify_ok_msg()
            self.__set_status('ready')

            self.stream = VideoStream(database.device)
            self.stream.enable_stream(self.__database.read('streaming'))

        else:
            self.__watch.unsubscribe()
            self.status = 'failed'


    def __on_snapshot_callback(self, snapshot, changes, read_time) -> None:

        for change in changes:

            # In case a attribute has changed
            if change.type.name == 'MODIFIED':

                incoming = change.document.to_dict()
                
                # Checks for status updates
                if incoming['status'] == 'disconnect':
                    self.__set_status('disconnect')

                # Custom commands: only continues if a client has modified the database
                if incoming['updated'] == 'None':
                    break

                match incoming['updated']:
                    
                    # Treats incoming gcodes
                    case 'command':
                        self.__set_status('busy')
                        commands = incoming['command'].split('_')

                        for code in commands:
                            # Send Command
                            self.__smart_send_command(code)
                            
                        self.__set_status('ready')

                    # Video stream control
                    case 'streaming':
                        self.stream.enable_stream(incoming['streaming'])

                    # Start printing routine
                    case 'status':
                        self.status = incoming['status']

                        if self.status == 'start-print':
                            self.__database.download_file()
                            self.__set_status('printing')
                            self.__start_print()
                        
                        # Others statuses are treated independently

                    # In case the baurate changed, disconnect printer to restart
                    case 'baudrate':
                        self.__set_status('disconnect')

                # Sinalizes that the update was received
                self.__database.update_database()

            # In case the printer was removed from database
            elif change.type.name == 'REMOVED':
                self.status = 'terminated'


    def __printing_thread(self) -> None:

        self.__set_status('printing')

        with open(System.local_print_file_path, 'r') as gcode:

            for code in gcode:

                # Cancels print
                if self.status == 'stop-print':
                    break
                
                # Awaits if the printing process was paused
                elif self.status == 'pause-print':
                    self.__set_status('paused')

                    while self.status not in ['resume-print', 'stop-print']:
                        continue
                    
                    if self.status == 'stop-print':
                        break    
                    else:
                        self.__set_status('printing')

                # Skip line if it only contains comments
                if code[0] == ';': 
                    continue

                # Removes comments on command lines
                elif code.__contains__(';'):
                    code = code.split(';')[0].strip()

                # Send Command
                self.__smart_send_command(code)
                
                # Syncronous temperature report manager
                if self.__has_queued_temperature_report:
                    self.__report_temperature()

        self.__set_status('ready')


    def __smart_send_command(self, code: str) -> None:
        # Wait for temperature
        if code.split(' ')[0] in ['M190', 'M109']:

            # Send command to set the temperature
            temperature_report = self.send_command(code)
            self.__report_temperature(temperature_report)
            
            # Awaits temperature to reach the set value
            while True:

                # Reads all the incoming echoes
                feedback = self.__printer_serial.read_all().decode()

                # If the heating process is done
                if self.__ok_msg in feedback:
                    break

                # Update database with the echo temperature data
                elif 'T:' in feedback:
                    for line in feedback.splitlines():
                        if 'T:' in line:
                            self.__report_temperature(line)
                            break
                        
                time.sleep(2)

        # Other commands
        else:                    
            # Send the current command
            feedback_msg: str = self.send_command(code)
            
            # Checks if the command was recognized/accepted by the printer
            if feedback_msg.__contains__(self.__ok_msg):
                return

            # If the printer was busy when the command was send
            elif feedback_msg.__contains__('busy'):

                # Awaits the current process to end
                while True:

                    # Awaits for an echo from the printer
                    while self.__printer_serial.in_waiting == 0:
                        time.sleep(0.05)
                    
                    echo = self.__printer_serial.read_all().decode()
                    
                    # Checks if the process has ended
                    if echo.__contains__(self.__ok_msg):
                        break


    def __queue_temperature_report(self) -> None:
        
        self.__has_queued_temperature_report: bool = False
        self.__temperature: dict() = {'heatbed': {'current': 0, 'setpoint': 0},
                                      'hotend' : {'current': 0, 'setpoint': 0}}
        
        while not self.status in ['terminated', 'disconnect']:

            if not self.__has_queued_temperature_report:            
                self.__has_queued_temperature_report = True

            # Does not send assyncronous commands to printer while printing
            if self.status != 'printing':            
                self.__report_temperature()

            time.sleep(5.0)


    def __report_temperature(self, report: str = 'null') -> None:
        
        temperature: dict() = {'heatbed': {'current': 0, 'setpoint': 0},
                               'hotend' : {'current': 0, 'setpoint': 0}}
        
        # Request temperature report
        if report == 'null':
            report = self.send_command("M105\n").split(' ')
        
        else:
            report = report.lstrip().split(' ')
            if report[0] != self.__ok_msg:
                report.insert(0, self.__ok_msg)

        # Command was recognized by the printer
        if report[0] == self.__ok_msg:

            temperature['hotend' ]['current' ] = round(float(report[1][2::]))
            temperature['hotend' ]['setpoint'] = round(float(report[2][1::]))
            temperature['heatbed']['current' ] = round(float(report[3][2::]))
            temperature['heatbed']['setpoint'] = round(float(report[4][1::]))  
            
            # If there has been any temperature changes
            if not all(temperature[key] == self.__temperature[key] for key in self.__temperature.keys()):
                
                self.__temperature = temperature
                self.__database.update_database(self.__temperature)

        self.__has_queued_temperature_report = False
                

    def __start_print(self) -> None:
        
        printing_thread = threading.Thread(target=self.__printing_thread)
        printing_thread.start()
    

    def __identify_ok_msg(self) -> str:

        # Waits for initialization
        while self.__printer_serial.in_waiting == 0:
            time.sleep(0.1)

        # Clears up the usart buffer
        self.__printer_serial.read_all()

        # Iterates to find printer feedback message
        while True:

            for k in range(10):
                self.__printer_serial.write("G0\n".encode())

            response_list = self.__printer_serial.read_all().decode().strip().split('\n')

            # Checks if the list has 10 itens, and all elemetns are the same
            if len(response_list) == 10 and all(item == response_list[0] for item in response_list):
                ok_msg = response_list[0]
                break
            
            time.sleep(0.1)

        # Clears up the usart buffer
        time.sleep(1.0)
        self.__printer_serial.read_all()

        return ok_msg


    def __set_status(self, _status: str) -> None:

        self.status = self.__database.update_status(_status)


    def send_command(self, msg: str) -> str:

        if msg[-1] != '\n':
            msg += '\n'

        # clean up serial buffer
        self.__printer_serial.read_all()

        self.__printer_serial.write(msg.encode())
        
        while self.__printer_serial.in_waiting == 0:
            time.sleep(0.05)
        
        response = self.__printer_serial.readline().decode()

        return response


    def run(self) -> None:
        """Keep alive loop"""

        # Start assyncronous temperature report
        temperature_report_thread = threading.Thread(target=self.__queue_temperature_report)
        temperature_report_thread.start()

        while not self.status in ['terminated', 'disconnect']:
            time.sleep(1)

        # Turn off steraming
        self.stream.enable_stream(False)

        # Terminate firebase connection
        self.__watch.unsubscribe()

        # Terminate serial
        self.__printer_serial.close()


    @staticmethod
    def __open_serial(com_port: str, baudrate: int) -> typing.Optional[serial.Serial]:

        try:
            return serial.Serial(port=com_port, baudrate=baudrate, timeout=1.0)

        except serial.SerialException:
            return None 
        
