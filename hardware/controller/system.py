import serial.tools.list_ports as port_list
import os
from id_generator import IDGenerator


class System:

    script_path = os.path.abspath(__file__)

    local_client_log_path = os.path.join(os.path.dirname(script_path), "resources/datalog.txt")
    local_print_file_path = os.path.join(os.path.dirname(script_path), "resources/printfile.gcode")

    @staticmethod
    def get_com_port(id: int) -> str:

        com_ports_list: list() = []

        for port, description, hwid in sorted(port_list.comports()): 
            if port != '/dev/ttyAMA0':
                com_ports_list.append(port)    

        try:
            return com_ports_list[id]
        except:
            return 'null'


    @staticmethod
    def get_data_log() -> tuple:
        """Reads the database log file and extracts user ID and device ID"""
        
        with open(System.local_client_log_path, 'r') as client_log:        
            log = client_log.readlines()
            user_id = log[0][5:-2]
            device_id = log[1][7:-1]   
	    
        return (user_id, device_id)


    @staticmethod
    def create_data_log(user: str='', device: str=IDGenerator.generate_id()) -> None:
        """Creates a new database log with the given user ID and device ID"""

        with open(System.local_client_log_path, 'w') as client_log:        
            client_log.truncate()
            client_log.write('user:{};\ndevice:{};'.format(user, device))


    @staticmethod
    def has_user() -> bool:
        """Verifies if the system has a user"""        
        return System.get_data_log()[0] != ''


    @staticmethod
    def has_data_log() -> bool:
        """Verifies if the system has a user"""        

        try:
            with open(System.local_client_log_path, 'r') as file:
                pass
        except:
            return False

        return True

