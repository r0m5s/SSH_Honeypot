# Honeypot Project
This project is a python built SSH Honeypot which proxies the SSH connection depending on the credentials used on the log in prompt.

Disclaimer: Major part of the code used was inspired from the user sjbell from the repository https://github.com/sjbell/basic_ssh_honeypot 

## Software Requirements
- VMWare Workstation >16 (Paid License) (or any Virtual Machine software such as VirtualBox, KVM, Windows Hypervisor)
- Cisco Modelling Labs 2.X (Paid License) (Optional)
- Python 3.X

## Additional Python Libraries
- paramiko

# Install Python Libraries Dependencies
## Linux
### Arch Based
`sudo pacman -S python python-pip python-paramiko`

### Debian Based
`sudo apt install python python-pip python-paramiko`

# Build Dependencies
`pip install --upgrade pip`

`pip install --upgrade -r paramiko`

Note: Windows and Mac where not tested

# Program Installation
## Steps to initiate the SSH Honeypot alone

Note: The steps are only valid if the system already has the correct dependencies installed and all commands were tested on a Linux OS

**IMPORTANT: Change the IP addresses inside the BasicsshHoneypot class to conform to your systems to be connected and the "passwords.txt" which contains the necessary passwords for login**

1. `git clone https://github.com/r0m5s/SSH_Honeypot`                              #Clones the git repo
2. `cd SSH_Honeypot`                                                              #Moves to the software directory
3. `ssh-keygen -t rsa -f server.key`                                              #Creates the public and private key for the honeypot
4. `mv server.key.pub server.pub`                                                 #Renames the public key 
5. `./ssh_honeypot`                                                               #Initiates the SSH Honeypot in port 2222 by default and locally 

**Optional**

6. `iptables -A PREROUTING -t nat -p tcp --dport 22 -j REDIRECT --to-port 2222`   #Forwards the port from 2222 to 22 (to avoid using the honeypot on the root user) 

## Steps to Install the Honeypot with CML Network

1. Download and install VMWare Workstation
2. Download the virtual machine containing the CML software and activate the software according to Cisco's instructions (The step to step installation of CML is out of the scope of these instructions)
3. Add a bridge interface called "bridge0" (or afterwards change the external connection to the respective interface name)
4. Open a browser (Chrome, Firefox, Brave, etc.)
5. Enter the IP address configured for the GUI of CML
6. Import the .yaml file from the folder to the CML Lab
7. Run the simulation
