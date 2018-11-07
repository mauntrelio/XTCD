# XTCD

**XFEL Tunnel Camera Drone**

XTCD (XFEL Tunnel Camera Drone) is a project about the design, test and implementation of tunnel inspection battery powered drones moving on rails, controlled with Raspberry Pis via a responsive web interface on the Wi-Fi network connection.

## Folder structure:

- **docs**: documentation
- **installation**: installation scripts and config template files
- **old_stuff**: old scripts and software used during the first development phase
- **scripts**: useful scripts
- **system**: core part of the software, contains the Python scripts to run the web server and operate the drone. This is the part that is going to be installed on the Raspberry Pi.

TODO: More specific information about the content of the **system** folder needs to be documented in detail.

## Dependencies:

- Python libraries:
	- RPiHTTPServer (web server with basic routing, authentication and static file management)
	- Adafruit PCA9685 (PWM board controller on I2C bus)
	- Adafruit ADS1x15 (Analog to digital converter on I2C bus)
	- pystache (html templates)
	- netifaces (network interfaces discovery)

- Other software
	- UV4L (https://www.linux-projects.org/uv4l/) (web streaming of video)
	- watchdog (optional) (restart in case of network problems, cpu overload, high temperature)

## Raspberry Pi configuration:

In order to create a RPi image to run XTCD, please read documentation in  
docs/XTCD - How to create a new image.md

TODO: Spefic configuration parameters of `system/config/*.json` files have to be documented yet.

## Contributing:

1. Fork it
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull / Merge Request 
