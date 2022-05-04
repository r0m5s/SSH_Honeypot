#!/usr/bin/env python3
import argparse
import threading
import socket
import sys
import os
import traceback
import logging
import json
import paramiko
import re
from datetime import datetime
from binascii import hexlify
from paramiko.py3compat import b, u, decodebytes

# Variables
HOST_KEY = paramiko.RSAKey(filename='server.key')
SSH_BANNER = "SSH-2.0-OpenSSH_7.7"
WELCOME_BANNER = "Welcome to Alpine Linux 23.03\r\n\r\n"

# Iniates global varibles for future change according to the credentials
local_ip_address = ""
local_port = 22
local_username = ""
local_password = ""

UP_KEY = '\x1b[A'.encode()
DOWN_KEY = '\x1b[B'.encode()
RIGHT_KEY = '\x1b[C'.encode()
LEFT_KEY = '\x1b[D'.encode()
BACK_KEY = '\x7f'.encode()

#Local Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='ssh_honeypot.log')

class BasicSshHoneypot(paramiko.ServerInterface):

    client_ip = None

    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        logging.info('client called check_channel_request ({}): {}'.format(
                    self.client_ip, kind))
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        logging.info('client called get_allowed_auths ({}) with username {}'.format(
                    self.client_ip, username))
        return "publickey,password"

    def check_auth_publickey(self, username, key):
        fingerprint = u(hexlify(key.get_fingerprint()))
        logging.info('client public key ({}): username: {}, key name: {}, md5 fingerprint: {}, base64: {}, bits: {}'.format(
                    self.client_ip, username, key.get_name(), fingerprint, key.get_base64(), key.get_bits()))
        return paramiko.AUTH_PARTIALLY_SUCCESSFUL

    def check_auth_password(self, username, password):

        global local_ip_address, local_port, local_username, local_password
        # Filters accepted passwords for login in the Protected Network
        passwords = list(open("passwords.txt"))
        for i in range(len(passwords)):
            passwords[i] = passwords[i].strip("\n")

        if password not in passwords:
            logging.info('new client credentials ({}): username: {}, password: {}'.format(self.client_ip, username, password))

            #Redirection to Honeypot System
            local_ip_address = "192.168.122.99"
            local_port = 22
            local_username = "rm"
            local_password = "rm"

            return paramiko.AUTH_SUCCESSFUL
        else:
            logging.info("Correct details detected, connecting to local computer")
            logging.info('new client credentials ({}): username: {}, password: {}'.format(self.client_ip, username, password))

            #Redirection to Protected Client
            local_ip_address = "127.0.0.1"
            local_port = 22
            local_username = "romas"
            local_password = "zezinho"

            return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command_text = str(command.decode("utf-8"))
        logging.info('client sent command via check_channel_exec_request ({}): {}'.format(self.client_ip, username, command))
        return True

def handle_cmd(cmd, chan, ip, client):

    output = ""
    if cmd != '':
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)

    # Reads the CLI output to a list
    stdout = stdout.readlines()

    # Outputs the CLI command to the client
    for line in stdout:
        chan.send(line)
        output += line

    if output != '':
        logging.info('Response from honeypot ({}):\n {}'.format(ip, output))


def handle_connection(client, addr):

    client_ip = addr[0]
    logging.info('New connection from: {}'.format(client_ip))

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        transport.local_version = SSH_BANNER # Change banner to appear more convincing
        server = BasicSshHoneypot(client_ip)
        try:
            transport.start_server(server=server)

        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            raise Exception("SSH negotiation failed")

        # wait for auth
        chan = transport.accept(10)
        if chan is None:
            print('*** No channel (from '+client_ip+').')
            raise Exception("No channel")

        # Closes the connection after X seconds (optional)
        #chan.settimeout(10)

        if transport.remote_mac != '':
            logging.info('Client mac ({}): {}'.format(client_ip, transport.remote_mac))

        if transport.remote_compression != '':
            logging.info('Client compression ({}): {}'.format(client_ip, transport.remote_compression))

        if transport.remote_version != '':
            logging.info('Client SSH version ({}): {}'.format(client_ip, transport.remote_version))

        if transport.remote_cipher != '':
            logging.info('Client SSH cipher ({}): {}'.format(client_ip, transport.remote_cipher))

        server.event.wait(10)
        if not server.event.is_set():
            logging.info('** Client ({}): never asked for a shell'.format(client_ip))
            raise Exception("No shell request")

        try:
            chan.send(WELCOME_BANNER)

            # Gets credentials to log in to the SSH system
            # The script makes the decision between the honeypot and client according to the user input
            global local_ip_address, local_port, local_username, local_password
            hostname = local_ip_address
            port = local_port
            user = local_username
            passwd = local_password

            # Start SSH connection to the Honeypot/Local Client
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, port=port, username=user, password=passwd)

            run = True
            while run:
                chan.send("[{}]$ ".format(hostname))
                command = ""
                while not command.endswith("\r"):
                    transport = chan.recv(1024)
                    print(client_ip+"- received:",transport)
                    # Echo input to psuedo-simulate a basic terminal
                    if(
                        transport != UP_KEY
                        and transport != DOWN_KEY
                        and transport != LEFT_KEY
                        and transport != RIGHT_KEY
                        and transport != BACK_KEY
                    ):
                        chan.send(transport)
                        command += transport.decode("utf-8")

                chan.send("\r\n")
                command = command.rstrip()
                logging.info('Command received ({}): {}'.format(client_ip, command))

                if command == "exit":
                    logging.info("Connection closed (via exit command): " + client_ip + "\n")
                    run = False

                else:
                    handle_cmd(command, chan, client_ip, client)

        except Exception as err:
            print('!!! Exception: {}: {}'.format(err.__class__, err))
            try:
                transport.close()
            except Exception:
                pass

        chan.close()

    except Exception as err:
        print('!!! Exception: {}: {}'.format(err.__class__, err))
        try:
            transport.close()
        except Exception:
            pass


def start_server(port, bind):
    """Init and run the ssh server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((bind, port))
    except Exception as err:
        print('*** Bind failed: {}'.format(err))
        traceback.print_exc()
        sys.exit(1)

    threads = []
    while True:
        try:
            sock.listen(100)
            print('Listening for connection ...')
            client, addr = sock.accept()
        except Exception as err:
            print('*** Listen/accept failed: {}'.format(err))
            traceback.print_exc()
        new_thread = threading.Thread(target=handle_connection, args=(client, addr))
        new_thread.start()
        threads.append(new_thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an SSH honeypot server')
    parser.add_argument("--port", "-p", help="The port to bind the ssh server to (default 2222)", default=2222, type=int, action="store")
    parser.add_argument("--bind", "-b", help="The address to bind the ssh server to", default="", type=str, action="store")
    args = parser.parse_args()
    start_server(args.port, args.bind)
