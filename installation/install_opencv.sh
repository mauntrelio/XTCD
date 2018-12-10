apt-get install build-essential cmake unzip pkg-config -y
apt-get install libjpeg-dev libpng-dev libtiff-dev -y
apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
apt-get install libxvidcore-dev libx264-dev -y 
apt-get install libgtk-3-dev -y
apt-get install libcanberra-gtk* -y
apt-get install libatlas-base-dev gfortran python2.7-dev -y

cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.0.zip
unzip opencv.zip
unzip opencv_contrib.zip
 	
mv opencv-4.0.0 opencv
mv opencv_contrib-4.0.0 opencv_contrib

pip install numpy

cd ~/opencv
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..

echo "CONF_SWAPSIZE=2048" > /etc/dphys-swapfile
/etc/init.d/dphys-swapfile stop
/etc/init.d/dphys-swapfile start

make -j4

make install
ldconfig

echo "CONF_SWAPSIZE=100" > /etc/dphys-swapfile
/etc/init.d/dphys-swapfile stop
/etc/init.d/dphys-swapfile start

cd /usr/local/lib/python2.7/site-packages/
ln -s /usr/local/python/cv2 cv2
echo "export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages" >> ~/.bashrc
source ~/.bashrc

pip install "picamera[array]"
