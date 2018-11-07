# XTCD - How to create a new image

Please note the following instructions refer to Raspbian Strecth as of October 2018.

## On a Desktop Ubuntu/Debian PC:

- Download Raspbian lite image from:

```bash
cd /tmp
mkdir -p /tmp/raspi
cd /tmp/raspi
wget https://downloads.raspberrypi.org/raspbian_lite_latest -O raspbian.img.zip
unzip raspbian.img.zip
mv *.img raspbian.img
```

### Mounting the image 

- Mount the image (it's an image of two partion, so you need losetup):

```bash
losetup -P /dev/loop0 raspbian.img
mkdir -p /mnt/raspimg
mount /dev/loop0p2 /mnt/raspimg
mount /dev/loop0p1 /mnt/raspimg/boot
```

The previous commands are supposed to be run as root (or with sudo)

### Optional: avoid that the filesystem is immediately resized on boot

- Edit cmdline.txt in boot partition by removing the argument

	`init=/usr/lib/raspi-config/init_resize.sh`

- Also remove the file

	`/mnt/raspimg/etc/init.d/resize2fs_once`

	and the symbolic link to it

	`/mnt/raspimg/etc/rc3.d/S01resize2fs_once`

### Setting up the Wi-Fi connection 

Copy `installation/config_resources/desy.pem` certificate into `/mnt/raspimg/etc/ca-certificates/`

Copy `installation/config_resources/wpa-supplicant.conf` into `/mnt/raspimg/etc/wpa-supplicant/`

Change the copied `wpa-supplicant.conf` in order to set up the correct passwords.

### Changing hostname

Edit hostname in `/mnt/raspimg/etc/hostname`

### Changing the root (and pi) password

Create a password for user pi using 

	mkpasswd -m sha-512 <newpassword> <salt> 

The salt value is a random string of your choice, anything will do.

Change the `/mnt/raspimg/etc/shadow` file with the new password above. Delete the string between the 1st and 2nd ‘:’ colons on the line starting with "root" (and "pi"). Paste in the new value between these colons.

### Activate SSH and set up ssh-keys


Place an empty file named 'ssh' onto the boot (FAT) partition

	touch /mnt/raspimg/boot/ssh

Put the content of your public key(s) in `/mnt/raspimg/root/.ssh/authorized_keys`

### Activate modules

Content of `/mnt/raspimg/boot/config.txt`

	dtparam=i2c_arm=on
	dtparam=spi=on
	enable_uart=1
	dtoverlay=w1-gpio

	# enable camera
	start_x=1
	gpu_mem=128

Content of `/etc/modules`

	i2c-dev
	cuse
	bcm2835_wdt


### Set up localization (keyboard and timezone)

Content of `/mnt/raspimg/etc/timezone`

	Europe/Berlin

Content of `/mnt/raspimg/etc/default/keyboard`

	XKBLAYOUT="us"


### Copy the installation script

The following command is referred to the current directory (XTCD/docs)
	
	cp ../installation/install_script.sh /mnt/raspimg/root/
	chmod a+x /mnt/raspimg/root/install_script.sh


### Create the SD card

**IMPORTANT**: replace /dev/sdX in the following command with whatever is your sd card

	umount /mnt/raspimg/
	dd if=/tmp/raspi/raspbian.img of=/dev/sdX bs=4M conv=fsync status=progress

----------------------------------------------------------------------------

## On the Raspberry	

Put the SD card in and boot the system up.

Log in as root, make sure the system is connected to the network, then run the install script:

	/mnt/raspimg/root/install_script.sh

The software is installed into `/var/XTCD`

After installation, adjust the config *.json files in `/var/XTCD/system/config` as needed.

Reboot.

Point your browser on the web address of the Raspberry Pi:

	http://raspberry-ip-address:service-port/

Enjoy!

-----------------------------------------------------------------------------

## Troubleshooting

If the service does not start (e.g. not reachable via web browser) do the following:

- Go to /var/XTCD/system
- Manually launch the script main.py and check the output

Be sure that the PWM board is **connected and powered** (this hardware component is needed for the system to start).

