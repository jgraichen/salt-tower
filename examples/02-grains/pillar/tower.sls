base:
  # You can include grains into include paths as well as filter on grains.
  #
  # This can be used to e.g. load default settings by a `region` or
  # share distribution depended values such as package names.

  # This will load files specific to a minions operating system release.
  #
  # e.g. a minion running on Ubuntu 18.04 will try to load `dist/bionic/*`.
  #
  - dist/{{ grains['oscodename'] }}/*.sls

  # We can use a grain matcher to match something specific.
  #
  - 'P@os:(RedHat|Fedora|CentOS)':
    - dist/redhat/*.sls

  # Each minion that has a configured region (e.g. custom grain)
  # should load some region defaults.
  #
  # We can use normal Python/Jinja to provide default values.
  #
  - region/{{ grains.get('region', 'none') }}/*.sls

