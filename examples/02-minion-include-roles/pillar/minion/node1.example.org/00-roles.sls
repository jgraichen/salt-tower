# This minion first shall include some shared roles.
#
# This can be archived by using an `include` list.
include:
- role/webserver

# The "included" pillar files will be merged into the pillar before this file
# but after this file is parsed. Therefore you can override values but cannot
# use them with Jinja here.
#
# You can use them in Jinja in the following files, e.g. 10-whatever.sls.

webserver:
  port: 8080
