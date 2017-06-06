#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPiHTTPServer import RPiHTTPServer, RPiHTTPRequestHandler
from drone import Drone
import socket
import pystache
import os
import json

class XTCDHandler(RPiHTTPRequestHandler):

  # GET /
  def default_response(self):
    tpl_vars = self.server.drone.status
    camera_url = self.server.config["CAMERA_URL"] % socket.gethostbyname(socket.gethostname())
    tpl_vars["CAMERA_URL"] = camera_url
    self.render_template(tpl_vars=tpl_vars)

  # GET /gallery 
  # TODO: to be done
  def gallery(self):
    self.render_template("gallery.html")

  # GET /config
  def show_config(self):
    self.render_template("config.html",self.config)

  # GET /arm
  # TODO: to be done
  def show_arm(self):
    self.render_template("arm.html")

  # POST /switch
  def switch(self):
    self.server.drone.toggle(self.server.config["RELAYS"][0])
    self.render_template()

  # POST /up
  def up(self):
    self.server.drone.up()
    self.render_template()

  # POST /down
  def down(self):
    self.server.drone.down()
    self.render_template()

  # POST /left
  def left(self):
    self.server.drone.left()
    self.render_template()

  # POST /right
  def right(self):
    self.server.drone.right()
    self.render_template()

  # POST /center
  def center(self):
    self.server.drone.center()
    self.render_template()

  # POST /forward
  def forward(self):
    self.server.drone.forward()
    self.render_template()

  # POST /back
  def back(self):
    self.server.drone.back()    
    self.render_template()

  # POST /stop
  def stop(self):
    self.server.drone.stop()    
    self.render_template()

  # POST /speedup
  def speedup(self):
    self.server.drone.speedup()  
    self.render_template()

  # POST /slowdown
  def slowdown(self):
    self.server.drone.slowdown()  
    self.render_template()

  # POST /picture
  # TODO: to be done
  def take_picture(self):
    self.render_template()

  # POST /arm
  # TODO: to be done
  def arm(self):
    self.render_template()

  # POST /save_config
  def save_config(self):
    self.render_template()

  def render_template(self, template="home.html", tpl_vars={}):
    if not tpl_vars:
      tpl_vars = self.server.drone.status

    if self.request_xhr:
      self.content_type = "application/json"
      self.content = json.dumps(tpl_vars)
    else:
      tpl = os.path.join(self.config["TEMPLATE_FOLDER"], template)
      if os.path.isfile(tpl):
        tpl_content = open(tpl,"r").read()
        self.content = pystache.render(tpl_content, tpl_vars)
      else:
        self.give_404("Template %s missing" % template)


def main():

  # read configuration from json
  basedir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(basedir,"config.json")

  # instantiate http server
  WebServer = RPiHTTPServer(config_file, XTCDHandler)

  # quick access to config params
  config = WebServer.server.config

  # assign variables to web server
  WebServer.server.drone = Drone(config) # instantiate drone controller
  WebServer.server.root_folder = basedir

  # start the web server
  try:
    print "Server listening on http://%s:%s" % (config["SERVER_ADDRESS"],config["SERVER_PORT"])
    WebServer.serve_forever()
  except KeyboardInterrupt:
    pass
    # TODO: cleanup pwm status on close
    WebServer.server.server_close()


if __name__ == '__main__':

  main()
