import sys

def vigenere_encrypt(password, message):
    message = message.upper()
    cipher_text = []
    
    size = len(password)
    for i in range(len(message)):
        if message[i] == " ":
            cipher_text.append(message[i])
        else:
            encrypted_letter = chr(((ord(message[i]) + ord(password[i % size])) % 26) + 65)
            cipher_text.append(encrypted_letter)
    
    return("".join(cipher_text))

def vigenere_decrypt(password, message):
    message = message.upper()
    original_text = []

    size = len(password)
    for i in range(len(message)):
        if message[i] == " ":
            original_text.append(message[i])
        else:
            encrypted_letter = chr(((ord(message[i]) - ord(password[i % size])) % 26) + 65)
            original_text.append(encrypted_letter)
    
    return("".join(original_text))
    

current_password = None;
action, message = sys.stdin.readline().rstrip().split(" ", 1)

while action != 'QUIT':
    if action == 'PASSKEY':
        current_password = message.upper()
        print("RESULT Success!")
        sys.stdout.flush()

    elif action == 'ENCRYPT':
        if current_password == None:
            print("ERROR No password set to encrypt!")
            sys.stdout.flush()
        else:
            encrypted_msg = vigenere_encrypt(current_password, message)
            print("RESULT {}".format(encrypted_msg))
            sys.stdout.flush()
        
    elif action == 'DECRYPT':
        if current_password == None:
            print("ERROR No password set to decrypt!")
            sys.stdout.flush()
        else: 
            decrypted_msg = vigenere_decrypt(current_password, message)
            print("RESULT {}".format(decrypted_msg))
            sys.stdout.flush()
            
    else:
        print ("ERROR The provided request is not supported by the program")

    # read the next action & message from the driver via standard input
    action, message = sys.stdin.readline().rstrip().split(" ", 1)

