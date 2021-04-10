# Installation

Salt Tower needs to be installed on the salt master to be available as an `ext_pillar` module.

The recommended installation methods are either via salts gitfs backend or with Pythons package manager `pip`.

## Salt GitFS

This method utilizes salts gitfs backend to directly load the tower module and renderers from this git repository. Ensure to follow the [gitfs setup guide](https://docs.saltproject.io/en/latest/topics/tutorials/gitfs.html).

Add the following to you salt master configuration, e.g. `/etc/salt/master.d/tower.conf`. It is recommended to pin to a specific version or commit, to avoid unexpected updates and because you need to sync all modules after any change.

```yaml
gitfs_remotes:
  - https://github.com/jgraichen/salt-tower.git:
      - base: v1.7.0
```

You need to sync all salt modules after installation and any upgrade:

```console
$ salt-run saltutil.sync_all
pillar:
    - pillar.tower
renderers:
    - renderers.filter
    - renderers.text
    - renderers.yamlet
```

This will make all modules (e.g. renderers) available to all minions too.

!!! warning
    All content from this repository will be "loaded" into your states tree, including any files from e.g. `test/`, `examples/`, `docs/` or the root directory.


## PIP Python Package

Salt Tower can be installed via the `pip` Python package manager too:

```console
$ pip install salt-tower
```

This will install Salt Tower as a Python package on the system, which is loaded by the salt processes.

!!! warning
    The tower modules (e.g. renderers) will only be available on the salt master or minion where the `salt-tower` package is installed. They are not automatically synced to any minion.
