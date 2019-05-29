# Include data files from other data files

The salt tower can include pillar files using a similar directive as in salt states. This examples demonstrates how this mechanism can be employed to have minion specific pillars include shared roles.

### Pillar

* [`minion/node1.example.org/00-roles.sls`](pillar/minion/node1.example.org/00-roles.sls)
* [`minion/node1.example.org/10-else.sls`](pillar/minion/node1.example.org/10-else.sls)
* [`role/webserver/init.sls`](pillar/role/webserver/init.sls)
* [`tower.sls`](pillar/tower.sls)

The pillar directory contains the tower pillar data and a tower top file for loading a minion specific pillar. This pillar data file will include a shared role while overriding

The `tower.sls` uses Jinja to load a minion specific pillar:

```yaml
  - minion/{{ minion_id }}/*.sls
```

This will load all pillar files from the directory with the minion ID. As files will be sorted you can prefix them with numbers to ensure proper overriding.

The first loaded files defines includes that will load a shared role pillar:

```yaml
include:
- role/webserver
```

This include will be loaded and merged after `00-roles.sls` has been parsed but before it is merged into the tower. It follows the normal lookup roles looking for `role/webserver`, `role/webserver.sls` and `role/webserver/init.sls`.

The role is loaded after `00-roles.sls` ash been parsed therefore we cannot e.g. use Jinja to access values:

```yaml
include:
- role/webserver

nginx:
  # This will NOT work
  port: {{ pillar.get('webserver:port') }}
```

It is possible to override values as the included files a merged upfront:

```yaml
include:
- role/webserver

webserver:
  port: 8080
```

You can also access values in any later file:

```yaml
# 00-roles.sls
include:
- role/webserver

# 10-nginx.sls
states:
- nginx

nginx:
  port: {{ pillar.get('webserver:port') }}
```
