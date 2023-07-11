import uuid
import hashlib


class IDGenerator:
    
    @staticmethod
    def __get_mac_address() -> str:

        try:
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)])
            return mac_address

        except (AttributeError, OSError):
            return None


    @staticmethod
    def __generate_hash(mac_address: str) -> str:

        # Remove ':' from MAC address and convert it to lowercase
        mac_address = mac_address.replace(':', '').lower()

        # Generate a hash using the MAC address
        hash = hashlib.md5(mac_address.encode()).hexdigest()

        # Take the first 12 characters of the hash and convert them to a decimal number
        # decimal_number = int(hash_value[:12], 16)

        # Format the decimal number as a 12-digit string
        #hash_sequence = '{:012d}'.format(decimal_number)

        return hash


    @staticmethod
    def generate_id() -> str:
        
        mac = IDGenerator.__get_mac_address()
        hash = IDGenerator.__generate_hash(mac)
        
        return hash



