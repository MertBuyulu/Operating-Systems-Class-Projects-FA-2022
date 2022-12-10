import sys
from datetime import datetime

# constructs a log message to be written out the output file
def create_log_message(action, message):
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime("%H:%M")
    return "{} [{}] {} {}\n".format(current_date, action, current_time, message)

# open the file for write
logFile = open(sys.argv[1], 'a')

initial_message = "Logging Started."
logFile.write(create_log_message(action="START",message=initial_message))

action, message = sys.stdin.readline().rstrip().split(" ", 1)

while action != 'QUIT':
    logFile.write(create_log_message(action=action, message=message))
    # read the next action & message from the driver via standard input
    action, message = sys.stdin.readline().rstrip().split(" ", 1)

closing_message = "Logging Stopped."
logFile.write(create_log_message(action="STOP", message=closing_message))

# close the log file 
logFile.close()
