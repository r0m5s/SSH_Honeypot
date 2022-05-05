# Virtual Honeypot Project
This project is a python built SSH Honeypot script built in python which proxies the SSH connection depending on the credentials used on the log in prompt to collect and log brute force attacks and other type of exploitation methods.

To use the script as a virtual honeypot, the project includes a .yaml file with pre-configured scripts and configurations that can be imported and used with Cisco Modelling Labs software.

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
`sudo apt install python3 python3-pip python3-paramiko`

Note: Windows and Mac operating systems where not tested

# Building Dependencies
`pip3 install --upgrade pip`

`pip3 install -r requirements.txt`

# Program Installation
## Steps to initiate the SSH Honeypot Script

Note: The steps are only valid if the system already has the correct dependencies installed and all commands were tested on a Linux OS

**IMPORTANT: Change the IP addresses inside the BasicsshHoneypot class to conform to your systems to be connected and the "passwords.txt" which contains the necessary passwords for login**

1. `git clone https://github.com/r0m5s/SSH_Honeypot`                              #Clones the git repo
2. `cd SSH_Honeypot`                                                              #Moves to the software directory
3. `ssh-keygen -t rsa -f server.key`                                              #Creates the public and private key for the honeypot
4. `mv server.key.pub server.pub`                                                 #Renames the public key 
5. `./ssh_honeypot`                                                               #Initiates the SSH Honeypot in port 2222 by default and locally 

**Optional:**

Assigning the port 22 requires root privileges and is not recommended to run the program on the root account in order to avoid security issues in case the attacker is able to exploit the software. Therefore the following line of iptables is recommended to redirect the traffic on port 22 to the port 2222. 

6. `iptables -A PREROUTING -t nat -p tcp --dport 22 -j REDIRECT --to-port 2222`

# Network Deployment
## Steps to Install the Honeypot with CML Network

1. Download and install VMWare Workstation
2. Download the virtual machine containing the CML software and activate the software according to Cisco's instructions - https://www.cisco.com/c/en/us/td/docs/cloud_services/cisco_modeling_labs/v200/quick/start/b_cml_quick_start_2-0/m_deploy_and_configure.html (Step to step installation of CML is out of the scope of these instructions)
3. Add a bridge interface called "bridge0" (or afterwards change the external connection to the respective interface name)
4. Open a browser (Chrome, Firefox, Brave, etc.)
5. Enter the IP address configured for the GUI of CML
6. Import the .yaml file from the folder to the CML Lab
7. Run the simulation

Any additional scripts and configurations should be already configured in the booting script in Alpine Linux systems and downloaded directly from the current github page. Therefore, if the booting scripts are being used instead of a pre-configured KVM Linux image, the simulation needs to have proper NAT and bridge configurations for external internet connection.

**Note: The installation of the ssh_honeypot.py program is automatically installed on the boot script from the .yaml file on the device called honeypot.**

## Network Tracking on router H-R1
In order to log all the traffic going inbound and outbound of the Honeypot Network the following commands are needed to filter the packets passing to the WAN.

After booting the router and accessing its command line interface enter the following commands:

1. `monitor capture buffer BF_HONEYNET size 512 max-size 128 circular`
2. `monitor capture point ip cef CP_HONEYNET gi0/1 both`
3. `monitor capture point associate CP_HONEYNET BF_HONEYNET`
4. `monitor capture point start CP_HONEYNET`

The integration of Cisco's Embedded Packet Capture can impact the performance of the edge router connected to the Honeypot Gateway due to the packet filtering and registration of the created buffer, therefore if a bigger network is created it is recommended to distribute the same line of commands between routers connected on different sections of the network. 

In order to verify if the router is filtering the packets the following should be used: `show monitor capture buffer BF_HONEYNET`

Finally, it is recommended to export the buffered packets to an external file sharing server implemented inside the Honeypot Network is proper security (could not be done due to time constraints): `monitor capture buffer BF_HONEYNET export [file sharing server Ipv4 address]`
