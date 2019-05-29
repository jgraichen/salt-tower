# Matching Grains for Region and Distribution

This example demonstrates how to use grains such as a region or the minions operating system to customize the generated pillar.

### Pillar

* [`dist/bionic/*.sls`](pillar/dist/bionic/)
* [`dist/redhat/*.sls`](pillar/dist/redhat/)
* [`region/eu-central-1/*.sls`](pillar/region/eu-central-1/)
* [`tower.sls`](pillar/tower.sls)

The pillar directory contains the tower pillar data and a tower top file for different minions operating systems and different regions. These files are conditionally loaded in `tower.sls` matching to minion grains.

The `tower.sls` uses Jinja replacements as well as compount matchers to load these files:

```yaml
  - dist/{{ grains['oscodename'] }}/*.sls
```

This simply inserts the grain values into the path that will be loaded.

```yaml
  - 'P@os:(RedHat|Fedora|CentOS)':
    - dist/redhat/*.sls
```

All matchers in `tower.sls` are compound matchers by default therefore we can select for specific values in a grain. Only minions with a matching grain will load the files from `dist/redhat/*`.

We can use all the usual power of Python and Jinja to insert grains e.g. using a default value in case the grain is absent:

```yaml
  - region/{{ grains.get('region', 'none') }}/*.sls
```
