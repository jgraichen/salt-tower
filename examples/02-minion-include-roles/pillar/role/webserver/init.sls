# This file is loaded when a minion includes `role/webserver`.

states:
- webserver

webserver:
  dir: /var/www
  port: 80
