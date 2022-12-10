Class: Fall 2022 - CS 4348.502
Student Name: Ahmet Mert Buyulu
Net ID: AMB190003
Date: 11/03/22

IDE CHOICE

    - I have not used an IDE to implement this project. I implemented it through the terminal via Vim.

FILES NAMES

    The project consists of only one python file:
        - bank_simulation.py
            1) This file simulates a bank containing Customer and Teller threads to interact with each other.
            2) The main program's thread instantiates three Teller threads and start their threads. 
            3) The main program's thread then instantiates 50 Customer threads and start their threads.
            4) Once steps 2 and 3 are completed, the bank gets opened (i.e. Customer threads will start interacting with the Tellers threads)
            4) It outputs the interactions between each customer and teller threads through the help of Semaphores to keep customer with tellers in sync. 
            5) The main program's thread waits on the completion of its sub threads until there is no more customer left to serve.
            6) Since there is no more customer left to serve, the bank gets closed and the program terminates successfully.

HOW TO COMPILE THE PROGRAM
    1) I have implemented the project in Python. Thus, it doesn't require any compilation.
    2) The program can be executed by running the following: "python3 bank_simulation.py"

