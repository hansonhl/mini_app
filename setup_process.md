# Setup process on CentOS Virtual Machine

## Download and install VirtualBox

VirtualBox website is https://www.virtualbox.org/

## Setup new CentOS7 virtual machine on VirtualBox

1. Download CentOS7 from one of the mirrors listed at
http://isoredirect.centos.org/centos/7/isos/x86_64/
2. Only download the **minimal** version
3. In VirtualBox, follow instructions to create new machine. No need to create
   a new user, root access is enough

## Internet configurations on CentOS7

This enables downloading packages from online and ssh access.

In the VM terminal:
1. `# vi /etc/sysconfig/network-scripts/ifcfg-xx`, where
   `xx = enp0s3` on my machine. Set the last line `ONBOOT=yes` instead of `no`.
2. `# service network restart`
3. `# yum install net-tools`
4. `# ifconfig` this will now show your local ip address.
5. Shut down the VM, and go to `VirtualBox -> [your CentOS machine] -> Settings
   -> Network.` Select `Bridged Adapter` for the "Attached to:" option.
6. Turn on the VM, and run `# ifconfig`. This will give you a new local IP    
   address, which you can use to ssh in.
7. The ubuntu terminal service in windows has ssh by default.
8. (on host machine terminal) `$ ssh root@<VM IP address>`

**Firewall configurations**

Configure firewall to allow browser and database gui software access from host
machine.

1. `# firewall-cmd --permanent --add-port=<port_number>/tcp`
2. `# firewall-cmd --reload`

`<port_number>=3306` for mysql server.

## Installing useful tools on CentOS7

1. `# yum install vim` to edit easily
2. `# yum install wget` to download things

## Setting up shared folder on CentOS7

Shared folders are convenient because you can use a text editor on your host
to edit files on your VM. Make sure you have a directory ready on your host to
share with the VM.

1. Go to `VirtualBox -> [your VM] -> Settings -> Storage`. Check that there is
   an empty entry under `Storage Devices -> Controller: IDE`. If not, click the
   icon with a round CD disk and a plus sign to add an optical drive, and choose
   `leave empty` in the popup window.
2. Boot the VM. In the top menu of the VM window, click on `Devices -> Insert
   Guest Additions CD Image...`. Now you will see that the empty entry in the
   `Storage Devices` panel mentioned now shows `VBoxGuestAdditions.iso`.
3. Reboot the VM.

In VM terminal (can be done using ssh access):
4. `# mkdir /mnt/cdrom`
5. `# mount /dev/cdrom /mnt/cdrom`
6. `# cp -R /mnt/cdrom /usr/local/src/VBoxAdditions`
7. `# yum install -y gcc gcc-devel gcc-c++ gcc-c++-devel make kernel kernel-devel bzip2`
8. `# cd /usr/local/src/VBoxAdditions`
9. `# ./VBoxLinuxAdditions.run install`
10. Shut down the VM.

Up to now we have properly set up the prerequisites to configure a shared
folder. To setup a shared folder that mounts automatically whenever you turn on
the VM, follow these steps:

11. Go to `VirtualBox -> [your VM] -> Settings -> Shared Folders`
12. Click on the "add folder" icon on the right side.
13. Enter/select the path to the folder on your **host machine** for the    
    `Folder Path` option.
14. Select `Auto-mount`.
15. Specify the path on the **VM** for the `Mount point:` option, i.e. where you
    want the shared folder to appear on the VM filesystem. I usually create a
    subdirectory in the `/mnt` directory.

## Installing Python3 on CentOS7

The imooc course gives a complicated method to install Python from source on
CentOS7. Here is an easier method:

In the VM terminal:
1. `# yum update -y`
2. `# yum install -y python3`
3. `# python3` to verify installation

**Setting up virtual environment**

See https://docs.python.org/3/tutorial/venv.html

1. `# python3 -m venv <env-name>`
2. `# source <path-to-env-dir>/bin/activate`
3. `# deactivate`

## Setting up MySQL database on CentOS7

**Installation**

1. `# yum remove mariadb-libs.x86_64` to remove database that is installed by
   default on CentOS7.
2. `# wget https://repo.mysql.com/mysql57-community-release-el7-8.noarch.rpm`
3. `# yum localinstall mysql57-community-release-el7-8.noarch.rpm`
4. `# yum install mysql-community-server`

**Initial setup**

5. `# service mysqld start` to start the mysql server
6. `# cat /var/log/mysqld.log | grep "password"` to get the password that is
   automatically generated to get root privilege access to the database
7. `# mysql -uroot -p` to login to the mysql server, enter the automatic    
   password above. Once you enter the server:
8. (optional) `mysql> set global validate_password_policy=0;`
9. (optional) `mysql> set global validate_password_length=1;`
   Run these two commands if you want a very simple password
10. `mysql> SET PASSWORD = PASSWORD('<your-password>');` to set password.

**Enable remote root access to server**

11. `mysql> update mysql.`user` set Host = '%' where User = 'root' and Host = 'localhost';`
12. `# service mysqld restart`
13. `# firewall-cmd --permanent --add-port=3306/tcp`
14. `# firewall-cmd --reload` The above to steps enables host access to the
    3306 port on the VM, which is the port for mysql.
