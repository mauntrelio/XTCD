# Install needed Python libraries

apt-get -y install python-pip

pip install RPiHTTPServer
pip install pystache
pip install netiface
pip install adafruit-pca9685
pip install adafruit-ads1x15
pip install Adafruit_DHT

# those are installed into
# usr/local/lib/python2.7/dist-packages

# Install UV4L for camera

curl http://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | apt-key add -

echo "deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" >> /etc/apt/sources.list

apt-get -y update
apt-get -y install uv4l uv4l-raspicam
apt-get -y install uv4l-raspicam-extras
apt-get -y install uv4l-server 

# apt-get -y  uv4l-uvc uv4l-xscreen uv4l-mjpegstream uv4l-dummy uv4l-raspidisp

service uv4l_raspicam restart

# Install watchdog

sudo modprobe bcm2835_wdt
echo "bcm2835_wdt" | sudo tee -a /etc/modules
apt-get -y install watchdog
update-rc.d watchdog defaults

# install additional software
apt-get -y install joe git i2c-tools

# Install camera_control XTCD
cd /var/
git clone https://github.com/mauntrelio/XTCD.git

# change the config *.json files

# script for startup in /etc/init.d/xtcd
cp /var/XTCD/installation/config_resources/init-script /etc/init.d/xtcd
chmod a+x /etc/init.d/xtcd
update-rc.d xtcd defaults

