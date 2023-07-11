from printer import Printer
from system import System
from firebase import FirebaseSignUp, FirebaseLogIn, Database


def main():

    # Log In Routine
    log_in = FirebaseLogIn()

    if not System.has_user() or not log_in.validade_device(*System.get_data_log()):
    
        sign_up = FirebaseSignUp()
    
        device_id = System.get_data_log()[1]        # Gets device id 
        sign_up.queue_device(device_id)             # Adds device to device queue in database
        user_id = sign_up.wait_for_user()           # Awaits user register
        sign_up.add_device()                        # Creates device register for the user
        System.create_data_log(user_id, device_id)  # Stores register log

    # Database and Printer Start Up
    while True:

        # Accesses the Firestore database with the registered user
        database = Database(*System.get_data_log())
        database.update_status('idle')

        # Awaits user confirmation to boot printer
        if not database.wait_user_request_to_boot():
            # In case waiting fails (user deleted)
            break

        # Printer Boot
        printer = Printer(System.get_com_port(0), database)

        if printer.status == 'failed':
            # Retry booting in case of failure
            continue

        # Run the printer if it was successfully booted
        printer.run()

        if printer.status == 'terminated':
            # Restart sign-up process if the database user was deleted
            break

        elif printer.status == 'disconnect':
            # Retry booting if the printer was disconnected
            continue


if __name__ == "__main__":
    
    while True:
        main()
