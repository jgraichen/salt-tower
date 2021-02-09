<p align="center"><img height="100" alt="Salt Tower (Logo)" src="./salt-tower.svg" /></p><br />

# Salt Tower - A Flexible External Pillar Module

[![GitHub Workflow Status (master branch)](https://img.shields.io/github/workflow/status/jgraichen/salt-tower/Python%20Package/master?logo=github)](https://github.com/jgraichen/salt-tower/actions?query=branch%3Amaster+workflow%3A%22Python+Package%22)

Salt Tower is an advanced and flexible `ext_pillar` that gives access to pillar values while processing and merging them, can render all usual salt file formats and include private and binary files for a minion.

Salt Tower is inspired by [pillarstack](https://github.com/bbinet/pillarstack) for merging pillar files and giving access to them. It also has a [top file](#top-file) like salt itself and utilizes salt renderers to supports all formats such as YAML, Jinja, Python and any combination. Supercharged [renderers for plain text and YAML](#yamlet-renderer) are included too.

Each tower data file is passed the current processed pillars. They can therefore access previously defined values. Data files can include other files that are all merged together.

Salt Tower is designed to completely replace the usual pillar repository or can be utilized beside salts original pillar that e.g. can bootstrap a salt master with Salt Tower.

## Questions or Need Help?

See [examples](examples/). They each have their own README further explaining the given example.

The is a [group](https://groups.google.com/d/forum/salt-tower) and [mailing list](mailto:salt-tower@googlegroups.com). You can join the group [here](https://groups.google.com/d/forum/salt-tower/join) or by sending a [subscribe email](mailto:salt-tower+subscribe@googlegroups.com).

Feel free to ask for help, discuss solutions or ideas there. Otherwise you can open an [issue](https://github.com/jgraichen/salt-tower/issues/new).

## Installation

#### GitFS

You can include this repository as a gitfs root and synchronize the extensions on the master:

```yaml
gitfs_remotes:
- https://github.com/jgraichen/salt-tower.git:
  - base: v1.4.0
```

Sync all modules:

```
$ salt-run saltutil.sync_all
pillar:
    - pillar.tower
renderers:
    - renderers.filter
    - renderers.text
    - renderers.yamlet
```

Please note that *everything* in this repository would be merged with your other roots.

#### pip

```
$ pip install salt-tower
```

#### Manual installation

Install the extension files from the `salt_tower/{pillar,renderers}` directories into the `extension_modules` directory configured in salt.

## Configuration

Salt Tower is configured as an `ext_pillar`:

```yaml
ext_pillar:
  - tower: /path/to/tower.sls
```

### Top File

The `tower.sls` file is similar to the usual `top.sls` with some important differences.

##### Ordered matchers

Pillar top items are ordered and processed in order of appearance. You can therefore define identical matchers multiple times.

```yaml
# tower.sls
base:
  - '*':
      - first

  - '*':
      - second
```

##### Common includes

You do not need to define a matcher at all, the files will be included for all minions. You also can use globs to match multiple files, e.g. include all files from `common/`.

```yaml
base:
  - common/*
```

##### Grains

The top file itself is rendered using the default renderer (`yaml|jinja`). Therefore you can use e.g. `grains` to include specific files.

```yaml
base:
  - common/*
  - dist/{{ grains['oscodename'] }}
```

##### Embedded data

You can directly include pillar data into the top file simply be defining a `dict` item.

```yaml
base:
  - '*.a.example.org':
      - site:
          id: a
          name: A Site
```

##### Iterative pillar processing

All matchers are compound matchers by default. As items are processes in order of appearance, later items can patch on previously defined pillar values. The above example includes `application.sls` for any minion matching `*.a.example.org` simply because it defines a `site` pillar value.

```yaml
base:
  - '*.a.example.org':
      - site: {id: a, name: A Site}

  - 'I@site:*':
      - applications
```

##### Late-bound variable replacement

File includes are pre-processed by a string formatter to late-bind pillar values.

```yaml
base:
  - '*.a.example.org':
      - site: {id: a, env: production}

  - '*.a-staging.example.org':
      - site: {id: a, env: staging}

  - 'I@site:*':
      - site/default
      - site/{site.id}
      - site/{site.id}/{site.env}/*
```

In the above example a minion `node0.a-staging.example.org` will include the following files:

```
site/default
site/a
site/a/staging/*
```

##### File lookup

File names will be matches to files and directories, e.g. when including `path/to/file` the first existing match will be used:

```
path/to/file
path/to/file.sls
path/to/file/init.sls
```

### Tower Data File

A data file is processed like a usual pillar file. Rendering uses salts template engines therefore all usual features should be available.

The injected `pillar` objects can be used to access previously defined values. The additional `.get` method allows to traverse the pillar tree.

```yaml
application:
  title: Site of {{ pillar.get('tenant:name') }}
```

**Note:** Using `salt['pillar.get']()` will *not* work.

Tower data files can be [any supported template format](https://docs.saltstack.com/en/latest/ref/renderers/) including python files:

```py
#!py

def run():
    ret = {'databases': []}

    for app in __pillar__['application']:
        ret['databases'].append({
            'name': '{0}-{1}'.format(app['name'], app['env'])
        })

    return ret
```

##### Includes

Pillar data files can include other pillar files similar to how states can be included:

```yaml
include:
  - another/pillar

data: more
```

Included files cannot be used in the pillar data file template itself but are merge in the pillar before the new pillar data. Includes can be relative to the current file by prefixing a dot:

```yaml
include:
  - file/from/pillar/root.sls
  - ./adjacent_file.sls
  - ../parent_file.sls
```

### Yamlet renderer

The Yamlet renderer is an improved YAML renderer that supports loading other files and rendering templates:

```yaml
ssh_private_key: !read id_rsa
ssh_public_key: !read id_rsa.pub
```

This reads a file from the pillar directory in plain text or binary and embeds it into the pillar. This eases shipping private files to minions.

Using the `!include` tag files can be pushed through salts rendering pipeline on the server:

```yaml
nginx:
  sites:
    my-app: !include ../files/site.conf
```

```
#!jinja | text strip
server {
  listen {{ pillar.get('my-app:ip') }}:80;
  root /var/www/my-app;
}
```

The pillar will return the following:

```yaml
nginx:
  sites:
    my-app: |
      server {
        listen 127.0.0.1:80;
        root /var/www/my-app;
      }
```

This can greatly simplify states as they only need to drop pillar values into config files and restart services:

```sls
nginx:
  pkg.installed: []
  service.running: []

{% for name in pillar.get('nginx:sites', {}) %}
/etc/nginx/sites-enabled/{{ name }}:
  file.managed:
    - contents_pillar: nginx:sites:{{ name }}
    - makedirs: True
    - watch_in:
      - service: nginx
{% endfor %}
```

The yamlet renderer `!include` macro does accept context variables too:

```yaml
nginx:
  sites:
    my-app: !include
      source: ../files/site.conf
      context:
        listen_ip: 127.0.0.1
```

```
#!jinja | text strip
server {
  listen {{ listen_ip }}:80;
  root /var/www/my-app;
}
```

### Text renderer

The text renderer (used above) renders a file as plain text. It stripes the shebang and can optionally strip whitespace from the beginning and end.

```
#!text strip

Hello World
```

This will return:

```
Hello World
```

The text renderer is mostly used for embedding rendered configuration files into a Yamlet file.

### Filter renderer

The filter renderer returns only a subset of data that matches a given grain or pillar key value:

```
#!yamlet | filter grain=os_family default='Unknown OS'

Debian:
  package_source: apt

RedHat:
  package_source: rpm

Unknown OS:
  package_source: unknown
```

When this file is rendered, only the data from the matching top level key is returned. The renderer supports glob matches and uses the minion ID by default:

```
#!yamlet | filter

minion-1:
  monitoring:
    type: ping
    address: 10.0.0.1

webserver-*:
  monitoring:
    type: http
    address: http://example.org
```

### Advanced usage (very dangerous)

The pillar object passed to the python template engine is the actual mutable dict reference used to process and merge the data. It is possible to modify this dict e.g. in a python template without returning anything:

```python
#!py

import copy

def run():
    databases = __pillar__['databases']
    default = databases.pop('default') # Deletes from actual pillar

    for name, config in databases.items():
        databases[name] = dict(default, **config)

    return {}
```

*Note 1:* Do not return `None`. Otherwise [Salt will render the template twice](https://github.com/saltstack/salt/blame/v2019.2.0/salt/template.py#L108) and all side-effects will be applied twice.

*Note 2:* The `__pillar__` object in Python templates is different to other template engines. It is a dict and does not allow to traverse using `get`.

```py
#!py

def run():
    return {
        'wrong': __pilar__.get('tenant:name'),
        'python': __pillar__['tenant']['name'],
        'alternative': tower.get('tenant:name')
    }
```

The above example demonstrates different usages. The first example will only work if the pillar contains an actual `tenant:name` top-level key. The second example is idiomatic-python but will raise an error if the keys do not exist. The third example uses the additional `tower` helper module to traverse the pillar data.

The `tower` pillar object is available in all rendering engines and can be used for low-level interaction with the ext_pillar engine. Some available functions are:

##### tower.get(key, default=None)

Get a pillar value by given traverse path:

```python
tower.get('my:pillar:key')
```

##### tower.update(dict)

Merges given dictionary into the pillar data.

```python
tower.update({'my': {'pillar': 'data'}})

assert tower.get('my:pillar') == 'data'
```

##### tower.merge(tgt, *objects)

Merges given dictionaries or lists into the first one.

Note: The first given dictionary or list is *mutated* and returned.

```python
tgt = {}

ret = tower.merge(tgt, {'a': 1})

assert ret is tgt
assert tgt['a'] == 1
```

##### tower.format(obj, *args, **kwargs)

Performs recursive late-bind string formatting using tower pillar and given arguments ad keywords for resolving. Uses `string.Formatter` internally.

```python
tower.update({
    'database': {
        'password': 'secret'
    }
})

ret = tower.format('postgres://user@{database.password}/db')

assert ret == 'postgres://user@secret/db'
```

Format accept dictionaries and list as well an can therefore be used to format full or partial pillar data, this can be used to e.g. format defaults with extra variables:

```python
#!py

def run():
    returns = {}
    defaults = __pillar__['default_app_config']
    # e.g. {
    #        'database': 'sqlite:///opt/{name}.sqlite'
    #        'listen': '0.0.0.0:{app.port}'
    # }

    for name, conf in __pillar__['applications'].items():
        # Merge defaults with conf into new dictionary
        conf = tower.merge({}, defaults, conf)

        # Format late-bind defaults with application config
        conf = tower.format(conf, name=name, app=conf)

        returns[name] = conf

    return {'applications': returns}
```
