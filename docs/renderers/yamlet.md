# Yamlet

The Yamlet renderer parses YAML and handles additional tags to work with files and blobs.

!!! note

    salt-tower will default to use `jinja|yamlet` as the default renderer stack if the `yamlet` renderer is installed. You do *not* need to explicit set the renderer e.g. with `#!yamlet`.

## Include a template file

The Yamlet renderer can include a template file into the pillar, without any formatting issues that might arrive when trying to use JINJA. The renderer will parse the YAML and directly render the template into the pillar, not the other way around.

The template file will be rendered

Assume we have an `nginx` state that expects a list of site configuration files as string blobs:

```yaml
# role/webserver/init.sls

nginx:
  site:
    default: !include files/nginx.default.j2
```

```jinja
#!jinja|text
# role/webserver/files/nginx.default.j2
# We want this file to be rendered using JINJA first, and into
# a text string second, to be included as a string in the pillar.

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    listen  443 ssl http2 default_server;
    listen  [::]:443 ssl http2 default_server;

    server_name {{ grains['localhost'] }};
    include snippets/snakeoil.conf;

    root /var/www/html;

    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        try_files $uri $uri/ =404;
    }
}
```

The `!include` tag will
