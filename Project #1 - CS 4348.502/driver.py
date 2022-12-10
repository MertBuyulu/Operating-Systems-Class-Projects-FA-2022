#!/usr/bin/env python
import re
import sys
from subprocess import PIPE, Popen

# a function to display history
def showHistory(history):
    print("\n  YOUR HISTORY \n------------------")
    for idx in range(len(history)):
        print("{}. {}".format((idx + 1), history[idx]))
    
    # give the user a way to exit from the history
    print("{}. go back".format(len(history) + 1))

def showHistoryContent(history):
    print("\n  YOUR HISTORY \n------------------")
    for idx in range(len(history)):
        print("{}. {}".format((idx + 1), history[idx]))

# do not store duplicate strings in the history for clarity
def updateHistory(history, sent, received):
    if history.count(sent) == 1:
        history.remove(sent)
    
    history.append(sent)
    response, returned_text = received.split(" ", 1)

    if response != "ERROR":
        if history.count(returned_text) == 1:
            history.remove(returned_text)
            
        history.append(returned_text)
    return history

def isValidCommand(command):
    # return false if the command contains any letters from the alphabet
    if re.search('[a-zA-Z]', command):
        return False
    num = int(command)

    # return false if the command is not in the specified range
    return num > 0 and num < 6

def getNextCommand(commands):
    print("\n    MAIN MENU\n------------------")
    for idx in range(len(commands)):
        print("{}. {}".format((idx + 1), commands[idx]))
    
    command = input("\nPlease select a command by entering a number between 1 and 5: ")
    if isValidCommand(command=command):
        return int(command) - 1
    else:
        command = input("\nError: Unknown command! Please select a command by entering a number between 1 and 5: ")
        while not isValidCommand(command=command):
            command = input("\nError: Unknown command! Please select a command by entering a number between 1 and 5: ")

        return int(command) - 1


# set the subprocesses and their stdin & stdout connections through pipes
logger = Popen(["python3", 'logger.py', sys.argv[1]], stdout=PIPE, stdin=PIPE, encoding='utf8')
encryption = Popen(["python3", 'encryption.py'], stdout=PIPE, stdin=PIPE, encoding='utf8')

history = []
commands = ["password", "encrypt", "decrypt", "history", "quit"]

print("---------------------- WELCOME TO THE PROGRAM ----------------------------")
index = getNextCommand(commands)

while commands[index] != "quit":

    if commands[index] == "password":

        choice = input("\nDo you want to use the history? [Y/N]: ")
        if choice == 'Y' or choice == 'y':

            if len(history) != 0:
                showHistory(history=history)
                choice = input("\nPlease select a string from the history to set as password: ")

                if (int(choice)) == (len(history) + 1):
                    password = input("\nPlease enter a new string to set as password: ")
                else:
                    password = history[int(choice) - 1]
            else:
                password = input("\nNo history found...Please enter a new string to set as password: ")
        else:
            password = input("\nPlease enter a new string to set as password: ")

        logger.stdin.write("PASSWORD SET {}\n".format(password))
        logger.stdin.flush()
                
        encryption.stdin.write("PASSKEY {}\n".format(password))
        encryption.stdin.flush()

        logger.stdin.write("PASSKEY SEND {}\n".format(password))
        logger.stdin.flush()   
        
        result = encryption.stdout.readline().rstrip()
        print("\n{}: {}".format(result.split(" ", 1)[0], result.split(" ", 1)[-1]))
        logger.stdin.write("PASSKEY {}\n".format(result))
        logger.stdin.flush()

    elif commands[index] == "encrypt":
        choice = input("\nDo you want to use the history? [Y/N]: ")

        if choice == 'Y' or choice == 'y':

            if len(history) != 0:
                showHistory(history=history)
                choice = input("\nPlease select a string from the history to encrypt: ")

                if (int(choice)) == (len(history) + 1):
                    text_to_be_encrypted = input("\nPlease enter a new string to encrypt: ")
                else:
                    text_to_be_encrypted = history[int(choice) - 1]

            else:
                text_to_be_encrypted = input("\nNo history found...Please enter a new string to entrypt: ")
        else:
            text_to_be_encrypted = input("\nPlease enter a new string to encrypt: ")

        encryption.stdin.write("ENCRYPT {}\n".format(text_to_be_encrypted))
        encryption.stdin.flush() 

        logger.stdin.write("ENCRYPT SEND {}\n".format(text_to_be_encrypted))
        logger.stdin.flush()   

        result = encryption.stdout.readline().rstrip()
        print("\n{}: {}".format(result.split(" ", 1)[0], result.split(" ", 1)[-1]))
        logger.stdin.write("ENCRYPT {}\n".format(result))
        logger.stdin.flush()

        # save the entered string
        history = updateHistory(history, text_to_be_encrypted, result)

    elif commands[index] == "decrypt":
        choice = input("\nDo you want to use the history? [Y/N]: ")

        if choice == 'Y' or choice == 'y':

            if len(history) != 0:
                showHistory(history=history)
                choice = input("\nPlease select a string from the history to decrpyt: ")

                if (int(choice)) == (len(history) + 1):
                    text_to_be_decrypted = input("\nPlease enter a new string to decrpyt: ")
                else:
                    text_to_be_decrypted = history[int(choice) - 1]
            else:
                text_to_be_decrypted = input("\nNo history found...Please enter a new string to decrpyt: ")
        else:
            text_to_be_decrypted = input("\nPlease enter a new string to decrpyt: ")

        encryption.stdin.write("DECRYPT {}\n".format(text_to_be_decrypted))
        encryption.stdin.flush()

        logger.stdin.write("DECRYPT SEND {}\n".format(text_to_be_decrypted))
        logger.stdin.flush()

        result = encryption.stdout.readline().rstrip()
        print("\n{}: {}".format(result.split(" ", 1)[0], result.split(" ", 1)[-1]))
        logger.stdin.write("DECRYPT {}\n".format(result))
        logger.stdin.flush()
        
        # save the entered string
        history = updateHistory(history, text_to_be_decrypted, result)

    elif commands[index] == "history":
        if len(history) != 0:
            showHistoryContent(history=history)
        else:
            print("\nNo history found")

        logger.stdin.write("HISTORY SHOW History\n")
        logger.stdin.flush()

    input("\nClick any key to continue the program: ")
    # read the next input from the user
    index = getNextCommand(commands)

encryption.stdin.write("QUIT quit program\n")
encryption.stdin.flush()
logger.stdin.write("QUIT quit program\n")
logger.stdin.flush()

logger.wait()
encryption.wait()

print("The program is now terminated...Bye!!")
