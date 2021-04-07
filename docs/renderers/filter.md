# Filter

The `filter` renderer takes a data structure, e.g. from the [Yamlet](../yamlet/) renderer, applies some filter based on the top-level keys and returns the first matching item.

## Example

By default, the `filter` renderer will match top-level keys with the salt minion ID from grains, but any grain can be specified:

### Minion ID

```yaml
#!yaml|filter grain=id
web_*:
  roles:
    - webserver

db_*:
  roles:
    - database

salt:
  roles:
    - salt/master

*.example.org:
  roles:
    - app
```

This example matches each top-level key with the `id` grain (the minion ID) and only returns the first matching data:

```yaml
# minion: web_03.example.org
roles:
  - webserver

# minion: db_a.example.org
roles:
  - database

# minion: blog.example.org
roles:
  - app
```


### Match a grain


The renderer can use any grain to match top-level keys:

```yaml
#!yaml | filter grain=os_family
Debian:
  repo_url: http://apt.example.org

RedHat:
  repo_url: http://rpm.example.org
```


### Match a pillar key

The `filter` renderer can match on a previously set pillar key too.

In this example the generic app server role loads a some custom values depending on the customer set previously.

!!! note

    The `filter` renderer is not restricted to being used with salt-tower on the master only, it can be used on the minion and in custom states too.

```yaml
#!yaml | filter pillar=site:customer
# roles/appserver/customer_config.yaml
customer_a:
  worker_count: 4

customer_b:
  worker_count: 8
```

```yaml
# tower.sls
base:
  - *.customerA.example.org:
      site:
        customer: customer_a

  - *.customerB.example.org:
      site:
        customer: customer_b

  - appserver-*:
      - roles/appserver.sls
```

```yaml
# roles/appserver.sls
application:
  install_dir: /opt/{{ tower.get("site:customer") }}/
  config: !include customer_config.yaml
```

This will result in the following output for minion `appserver-7.customerA.example.org`:

```yaml
application:
  install_dir: /opt/customer_a/
  config:
    worker_count: 4

site:
  customer: customer_a
```


### Default value

If a grain or pillar doesn't exist, a default value can be given to match the top-level keys:

```yaml
#!yaml | filter pillar=site:customer default=demo

customer_a:
  worker_count: 4

customer_b:
  worker_count: 8

demo:
  worker_count: 1
```

## Technical details

### Arguments

The `filter` renderer can take values from grains or the pillar, the key has to be specified on the shebang:

```
#!filter pillar=some:key
```

or

```
#!filter grain=os_family
```

A default value can be specified for both, if the grain or pillar key does not exist, the default value will be used for matching the top-level keys. The default value must be specified with quotes if it contains spaces.

```
#!filter pillar=some:key default=value
#!filter grain=id default='value with space'
```

!!! note

    Arguments are parsed using Pythons [`shlex.split`](https://docs.python.org/3/library/shlex.html#shlex.split), therefore the usual shell-style escape rules apply to values.

## Pattern matching

Top-level keys are matched to the grain or pillar values using Pythons [`fnmatch.fnmatch`](https://docs.python.org/3/library/fnmatch.html) function. Only the first matching item is returned, otherwise an empty dictionary.

See [`test/renderers/test_filter.py`](https://github.com/jgraichen/salt-tower/blob/main/test/renderers/test_filter.py) for more examples and detailed behavior.
