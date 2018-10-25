# XTCD

**XFEL Tunnel Camera Drone**

XTCD (XFEL Tunnel Camera Drone) is a project about the design, test and implementation of tunnel inspection battery powered drones moving on rails, controlled with Raspberry Pis via a responsive web interface on the Wi-Fi network connection.

## Folder structure:

- **docs**: documentation
- **installation**: installation scripts and config template files
- **old_stuff**: old scripts and software used during the first development phase
- **scripts**: useful scripts
- **system**: core part of the software, contains the Python scripts to run the web server and operate the drone. This is the part that is going to be installed on the Raspberry Pi.

## Dependencies:

- Python libraries:
	- RPiHTTPServer
	- Adafruit PCA9685
	- pystache
	- netifaces

- Other software
	- UV4L (https://www.linux-projects.org/uv4l/)
	- watchdog (optional)

## Raspberry Pi configuration:

To be documented...

## Contributing:

1. Fork it
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request
