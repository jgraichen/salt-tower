# Configuration

Salt Tower is set up and configured in the salt master configuration. See salts [`ext_pillar` documentation](https://docs.saltproject.io/en/latest/topics/development/modules/external_pillars.html) for details about external pillar modules.

The `tower` external pillar modules only needs one or more tower files for configuration:

```yaml
# /etc/salt/master.d/tower.conf

ext_pillar:
  - tower: /path/to/tower.sls
```

