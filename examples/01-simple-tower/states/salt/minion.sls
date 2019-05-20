salt-minion:
  pkg.installed: []
  service.running: []

/etc/salt/minion.d/common.conf:
  file.serialize:
    - dataset_pillar: salt:minion
    - formatter: yaml
    - watch_in:
      - service: salt-minion
    - require_in:
      - service: salt-minion
