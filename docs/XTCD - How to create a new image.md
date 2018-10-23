# XTCD - How to create a new image

Please note the following instructions refer to Raspbian Strecth as of October 2018.

## On a Desktop Ubuntu/Debian PC:

- Download Raspbian lite image from:
	cd /tmp
	mkdir -p /tmp/raspi
	cd /tmp/raspi
	wget https://downloads.raspberrypi.org/raspbian_lite_latest -O raspbian.img.zip
	unzip raspbian.img.zip
	mv *.img raspbian.img

### Mounting the image 

- Mount the image (it's an image of two partion, so you need losetup):
	losetup -P /dev/loop0 raspbian.img
	mkdir -p /mnt/raspimg
	mount /dev/loop0p2 /mnt/raspimg
	mount /dev/loop0p1 /mnt/raspimg/boot

### Optional: avoid that the filesystem is immediately resized on boot

- Edit cmdline.txt in boot partition by removing the argument

	init=/usr/lib/raspi-config/init_resize.sh

	Also remove the file

	/mnt/raspimg/etc/init.d/resize2fs_once

	and the symbolic link to it

	/mnt/raspimg/etc/rc3.d/S01resize2fs_once

### Setting up the Wi-Fi connection 

Copy desy.pem certificate into /mnt/raspimg/etc/ca-certificates/
Copy wpa-supplicant.conf into /mnt/raspimg/etc/wpa-supplicant/

Change the copied wpa-supplicant.conf in order to set up the correct passwords.

### Changing hostname

Edit hostname in /mnt/raspimg/etc/hostname

### Changing the root (and pi) password

Create a password for user pi using 

	mkpasswd -m sha-512 <newpassword> <salt>. 

The salt value is a random string of your choice, anything will do.

Change the /mnt/raspimg/etc/shadow file with the new password above. Delete the string between the 1st and 2nd ‘:’ colons on the line starting with "root" (and "pi"). Paste in the new value between these colons.

### Activate SSh and set up ssh-keys

Put the content of your public key(s) in /mnt/raspimg/root/.ssh/authorized_keys

### Activate modules

/mnt/raspimg/boot/config.txt

	dtparam=i2c_arm=on
	dtparam=spi=on
	enable_uart=1
	dtoverlay=w1-gpio

	# enable camera
	start_x=1
	gpu_mem=128

/etc/modules

	i2c-dev
	cuse
	bcm2835_wdt


### Set up localization (keyboard and timezone)

/mnt/raspimg/etc/timezone

	Europe/Berlin

/mnt/raspimg/etc/default/keyboard

	XKBLAYOUT="us"

=======================================================

## On the Raspberry	