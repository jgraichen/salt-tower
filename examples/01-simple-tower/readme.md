# Simple Tower Pillar Example

This examples demonstrates a simple tower pillar with some exemplary states. It will demonstrate the basic tower pillar features and how this simplifies states and makes them much easier to reuse.

The example states consists of `salt/minion.sls`, a simple state to install and configure the salt minion, and `nginx/init.sls`, installing and configuring a Nginx web server with multiple sites.

The pillar directory contains the tower pillar data and a tower top file for multiple web minions with one special node. The salt master must be configured to use the tower ext_pillar from the example:

```
# /etc/salt/master.d/tower-example.conf
ext_pillar:
- tower: /path/to/example/pillar/tower.sls
```

Start exploring the example with the `pillar/tower.sls` file, try to following what pillar data files are included.

---

A rendered pillar for the salt minion `web2.example.org` would look similar to this:

```yaml
states:
- salt/minion
- nginx

salt:
  minion:
    hash_type: sha256
    state_output: changes

nginx:
  sites:
    default: |
      # We need the shebang above to first render this file with Jinja and secondly
      # "convert" it to plain text striping the shebang itself and extra whitespace.

      server {
          listen 80;

          # Insert the hosts FQDN here using Jinja and grains
          server_name {{ grains['fqdn'] }};

          root /var/www/html;
          index index.html;
      }

    www: |
      server {
          listen 80;

          server_name www.example.org;

          root /var/www/web2;
          index index.html;
      }

    web2: |
      # Just some hand written, readable, pure nginx configuration.

      server {
          listen 80;

          server_name web2.example.org;

          root /home/web2/special_content;
          index index.html;
      }
```

The `states/top.sls` would therefore expand to this:

```yaml
base:
  web2.example.org:
    - salt/minion
    - nginx
```

Try following the example states and imaging what they would do. All they need
to do now is installing packages, dropping some text blobs are configuration files and starting services.
