# Salt Tower

Advanced and flexible `ext_pillar` that gives access to pillar values while processing, provides merge functionality and utilizes salts own template engines.

Salt tower is inspired by [pillarstack](https://github.com/bbinet/pillarstack) and uses its merging implementation. It reuses the concept of a top file and utilizes salt renderers. Therefore Salt Tower supports all engines including YAML, Jinja and Python, as well as chaining engines together.

Each tower data file is passed the current processed pillars. Their can therefore access previously defined values.

Salt Tower is designed to completely replace the usual pillar repository.

Installation
------------

Install Salt Tower by dropping the `tower.py` in the `<extension_modules>/pillar` directory.

Configuration
-------------

Salt Tower is configured as an `ext_pillar`:

```yaml
ext_pillar:
  - tower: /path/to/tower.sls
```

The tower file is similar to the usual `top.sls` with some important differences.

```yaml
base:
  - '*':
      - first

  - '*':
      - second
```

Pillar top items are ordered and processed in order of appearance. You can therefore define identical matchers multiple times.

```yaml
base:
  - common/*
```

You do not need to define a matcher at all, the files will be included for all minions. You also can use globs to match multiple files, e.g. include all files from `common/`.

```yaml
base:
  - common/*
  - dist/{{ grains['oscodename'] }}
```

The top file itself is rendered using the default renderer (`yaml|jinja`). Therefore you can use e.g. `grains` to include specific files.

```yaml
base:
  - '*.a.example.org':
      - site:
          id: a
          name: A Site
```

You can directly include pillar data into the top file simply be defining a `dict` item.

```yaml
base:
  - '*.a.example.org':
      - site: {id: a, name: A Site}

  - 'I@site:*':
      - applications
```

All matchers are compound matchers by default. As items are processes in order of appearance, later items can patch on previously defined pillar values. The above example includes `application.sls` for any minion matching *.a.example.org` simply because it defines a `site` pillar value.

```yaml
base:
  - '*.a.example.org':
      - site: {id: a, env: production}

  - '*.a-staging.example.org':
      - site: {id: a, env: staging}

  - 'I@site:*':
      - site/default
      - site/{site.id}
      - site/{site.id}/{site.staging}/*
```

File includes are pre-processed by a string formatter to late-bind pillar values. In the above example a minion `node0.a-staging.example.org` will include the following files:

```
site/default
site/a
site/a/staging/*
```

Includes will be matches to files and directories, e.g. when including `path/to/file` the first existing match will be used:

```
path/to/file
path/to/file.sls
path/to/file/init.sls
```
