import socket
import threading
import random
import math
import json

def isPrime(n):   # Function to determine whether n is prime or not
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def gcd(m, n):             #Function to check whether GCD is 1 or not
    return math.gcd(m, n) == 1

def generate_keys():        #Implementation of RSA algorithm

    primes = [i for i in range(100, 1000) if isPrime(i)]    #Selecting 2 large prime numbers
    p = random.choice(primes)
    primes.remove(p)
    q = random.choice(primes)

    n = p * q
    phi_n = (p - 1) * (q - 1)       #Calculating totient's function

    e = random.randint(2, phi_n - 1)
    while not gcd(phi_n, e):
        e = random.randint(2, phi_n - 1)

    d = pow(e, -1, phi_n) 

    return (n, e), (n, d)       # n,e: public key  n,d: private key

def encrypt(message, public_key):   #encrypting plain-text message using RSA
    n, e = public_key
    cipher = [pow(ord(char), e, n) for char in message]
    return cipher

def decrypt(cipher, private_key):   #decrypting the cipher and joining as string
    n, d = private_key
    message = [chr(pow(c, d, n)) for c in cipher]
    return ''.join(message)

def sending_messages(c, partner_public_key):    #sending message over socket connection
    while True:
        message = input("")
        encrypted_message = encrypt(message, partner_public_key)    #encrypting using partner's public key
        encrypted_message_json = json.dumps(encrypted_message)
        c.send(encrypted_message_json.encode('utf-8'))      #sending json encoded message
        print("You: " + message)

def receiving_messages(c, private_key):     #receiving and decrypting messages
    while True:
        encrypted_message_json = c.recv(4096).decode('utf-8')
        encrypted_message = json.loads(encrypted_message_json)
        message = decrypt(encrypted_message, private_key)       #decrypt using private key
        print("Partner: " + message)

choice = input("Do you want to host(1) or connect to server(2)? ")

if choice == "1":

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("172.31.16.1", 9999))
    server.listen()

    print("Waiting for connection...")
    client, _ = server.accept()
    print("Connected to client")

    public_key, private_key = generate_keys()

    client.send(json.dumps(public_key).encode('utf-8'))
    partner_public_key = json.loads(client.recv(4096).decode('utf-8'))

elif choice == "2":

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("172.31.16.1", 9999))

    public_key, private_key = generate_keys()

    partner_public_key = json.loads(client.recv(4096).decode('utf-8'))
    client.send(json.dumps(public_key).encode('utf-8'))

else:
    exit()

# Start sending and receiving threads
threading.Thread(target=sending_messages, args=(client, partner_public_key)).start()
threading.Thread(target=receiving_messages, args=(client, private_key)).start()
