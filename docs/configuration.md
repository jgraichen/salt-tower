# Configuration

Salt Tower is set up and configured in the salt master configuration. See salts [`ext_pillar` documentation](https://docs.saltproject.io/en/latest/topics/development/modules/external_pillars.html) for details about external pillar modules.

The `tower` external pillar modules only needs one or more tower files for configuration:

```yaml
# /etc/salt/master.d/tower.conf

ext_pillar:
  - tower: /path/to/tower.sls
```

## Feature flags

Salt Tower behavior can be twisted a bit using feature flags. They can be set in the salt master configuration file.

### include_directory_mode

The `include_directory_mode` flag changes the behavior when including files from a directory. The default mode `"init"` works just like expected.

When including a file such as `role/openssh`, Salt Tower will look for the following files and pick the first one that exists:

1. `role/openssh`
2. `role/openssh.sls`
3. `role/openssh/init.sls`

An alternative mode can be enabled by setting `include_directory_mode` to `"all-sls"`:

```yaml
# /etc/salt/master

salt_tower.include_directory_mode: all-sls
```

Salt Tower will now look if `role/openssh` is a directory. If that is the case, it will include all `*.sls` files in that directory, ordered by filename:

1. `role/openssh/10-config.sls`
2. `role/openssh/20-ciphers.sls`

When no files are found in that directory, it will proceed with the same lookup roles as before.

The `all-sls` mode can be quite useful if you like to split up e.g. your roles, or minion overrides into multiple, ordered files, for example to use different renderers.

!!! example

    Imagine you want to configure `openssh` for your servers and you want to ship distribution specific settings for e.g. allowed ciphers. Servers running `openssh` are currently including `role/openssh`, that contains the shared config, and you do not want to add role details to your `tower.sls`, or update the include statement for each server.

    Using the `salt_tower.include_directory_mode: all-sls` mode, you can simply replace your `role/openssh.sls` or `role/openssh/init.sls` with a directory, and, for example, use the `filter` renderer to only add the specific bits needed:

    ```yaml title="role/openssh/10-config.sls"
    # Shared config for all openssh daemons

    openssh:
      server:
        config:
          Port: 22
          Protocol: 2
          HostKey: [/etc/ssh/ssh_host_ed25519_key]
          # ...
    ```

    ```yaml title="role/openssh/11-ciphers.sls"
    # yaml | filter grain=oscodename

    # Restrict key exchange, cipher, and MAC algorithms, as per sshaudit.com
    # hardening guide.

    bionic: # Ubuntu 18.04
      openssh:
        server:
          config:
            Ciphers: chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
            HostKeyAlgorithms: ssh-ed25519,ssh-ed25519-cert-v01@openssh.com
            KexAlgorithms: curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha256
            MACs: hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,umac-128-etm@openssh.com

    focal: # Ubuntu 20.04
      openssh:
        server:
          config:
            Ciphers: chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
            HostKeyAlgorithms: ssh-ed25519,ssh-ed25519-cert-v01@openssh.com,sk-ssh-ed25519@openssh.com,sk-ssh-ed25519-cert-v01@openssh.com,rsa-sha2-256,rsa-sha2-512,rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-512-cert-v01@openssh.com
            KexAlgorithms: curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha256
            MACs: hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,umac-128-etm@openssh.com
    ```

    The servers will now a all share the same configuration, but will have different cipher settings depending on their operating system version.

### salt_tower.raise_on_missing_files

Enabling the `salt_tower.raise_on_missing_files` flag will have salt tower raise an error if any included file from `tower.sls` or any `include` list cannot be found. If the include statement is a pattern, that does not match any files, an error will be raised too.

Includes in the top `tower.sls` can be marked as optional using the special `!optional` YAML tag:

```yaml title="tower.sls"
base:
  - common/*

  # Optional minion-specific overrides
  - !optional minion/{{ minion_id }}
```

### salt_tower.unstable_enable_saltenv

The `salt_tower.unstable_enable_saltenv` flag modifies some options passed to the salt rendering pipeline. The salt renderers behave differently if they think they are rendering a state file or a pillar file. Including a file, such as with JINJA `import_yaml` will look up files in either `file_roots` or `pillar_roots`. Unfortunately, this behavior cannot be customized by plugins.

By setting `salt_tower.unstable_enable_saltenv` to `True`, Salt Tower will pass additional flags to the rendering pipeline, indicating that pillars are rendered. Engines, such as JINJA, will now look up files in `pillar_roots`. This can work well, when you Salt Tower base directory is the same as the pillar root directory.

See issue [#11](https://github.com/jgraichen/salt-tower/issues/11) for more details.

### salt_tower.enable_inventory

**Experimental feature**: Enables the `inventory` mode. All pillar data within the `inventory:` subtree will not be returned in the final result. Instead, an additional context module is passed to templates, easing access to minion-scoped variables.

This _inventory_ can be used to provide specialized, independent variable values to other pillar files such as roles. See the following example:

```yaml title="tower.sls"
base:
  - inventory/*
  - 'web*'
      - role/web
```

```yaml title="inventory/vars.sls"
inventory:
  web-0:
    ip:
      public: 203.0.113.100
    nginx:
      server_name: example.org

  web-1:
    ip:
      public: 203.0.113.110
    nginx:
      server_name: example.com
```

```yaml title="role/web.sls"
states:
  - nginx

nginx:
  config: |
    server {
      listen {{ inventory.get('ip:public') }}:80;
      server_name {{ inventory.get('nginx:server_name') }};
    }
```

The inventory can provide custom variables to be used in larger pillar files, or used in multiple roles.
