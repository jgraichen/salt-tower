# Yamlet

The Yamlet renderer parses YAML and handles additional tags to work with files and blobs.

!!! note

    salt-tower will default to use `jinja|yamlet` as the default renderer stack if the `yamlet` renderer is installed. You do *not* need to explicit set the renderer e.g. with `#!yamlet` to use its features in tower data files.


## YAML

The Yamlet renderer parses a text file as YAML and returns the resulting data structure. The return value of this renderer therefore is a dict, or list, or similar, but not text.

Additional YAML tags are processed to safely load and include files, e.g. text config files or binary files as blobs, without issues with YAML formatting or encoding compared to including them with JINJA.

`!include`
: [Include a template file](#include-a-template-file) into the YAML data structure, e.g. a web server or application config file.

`!read`
: [Directly load and include a file](#include-a-binary-file) without further processing. Can be a text or a binary file, e.g. a TLS private key or a binary license file.

See the following sections for details.


## Examples

### Include a template file

The Yamlet renderer can include a template file into the pillar, without any formatting issues that might arrive when trying to use JINJA. The renderer will parse the YAML and directly render the template into the pillar, not the other way around.

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

The `!include` tag will render the file using the default salt renderers. You can therefore use JINJA or any other renderers. It is recommended to specify the renderers using a shebang as shown above:

```
#!jinja|text
```

This will first render the file using the JINJA, replacing e.g. `#!jinja {{ grains['localhost'] }}`, and return the result as a text to the yamlet renderer.

!!! note

    Read more about salts rendering pipeline and how to combine renderers in the [official documentation](https://docs.saltproject.io/en/master/ref/renderers/index.html).

The result will look like this, but there will be no issue with indention, encoding, formatting or anything else:

```yaml
nginx:
  site:
    default: |
      # role/webserver/files/nginx.default.j2
      # We want this file to be rendered using JINJA first, and into
      # a text string second, to be included as a string in the pillar.

      server {
          listen 80 default_server;
          listen [::]:80 default_server;

          listen  443 ssl http2 default_server;
          listen  [::]:443 ssl http2 default_server;

          server_name server-hostname-here;
          include snippets/snakeoil.conf;

          root /var/www/html;

          location / {
              # First attempt to serve request as file, then
              # as directory, then fall back to displaying a 404.
              try_files $uri $uri/ =404;
          }
      }
```

This can greatly simplify writing states, as is much easier to just ship full configuration files or snippets.


### Custom template context

The longer mapping variant of the `!include` tag allows passing custom context data to the renderers. This can be used to expand e.g. a shared configuration file snippet with some custom values:

```yaml
# role/webserver/init.sls

nginx:
  site:
    app1: !include
      source: files/nginx.app.j2
      context:
        server_name: app1.com
        directory: sites/app1

    app2: !include
      source: files/nginx.app.j2
      context:
        server_name: app2.com
        directory: app2/public
```

```jinja
#!jinja|text
# role/webserver/files/nginx.app.j2

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name {{ server_name }};

    root /var/www/{{ directory }};

    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        try_files $uri $uri/ =404;
    }
}
```


### Include a data file

The result of a template file doesn't have to a string, it can be data too. You can e.g. include one YAML file into multiple pillar files, or combine that with the [filter renderer](../filter/), to include data from a shared set.

The following example shows to include a shared YAML dataset into multiple places, without any parsing or indention errors, as can happen when using the JINJA `include` directive:

```yaml
#!yaml
# Shared data set (dataset.yaml)

key: 1
```

```yaml
# A pillar data file
application_1:
  config: !include ../dataset.yaml

application_2:
  config: !include ../dataset.yaml
```

The result will have the data set loaded and included for both application keys:

```yaml
application_1:
  config:
    key: 1

application_2:
  config:
    key: 2
```


### Include a binary file

The `!read` YAML tag can safely load text or binary files and include them as blobs in the result.

```yaml
application:
  license_file: !read files/license.bin
```

The `license.bin` file can be any kind of file, even a binary file. The Yamlet renderer will load the file *after* it has parsed the YAML and safely embed the binary file content into the data result.

!!! note

    The resulting data structure will include file content as binary string, not a Unicode string as everything else, e.g.:

    ```python
    pillar['key'] == b"jd\x81\xed\xa2~*\xca6\xd88,\x15zr\xb6"
    ```

    Salt internal and most states (e.g. `file.managed`) should have not problem with that, but custom code might need adjustments if it e.g. processes the content and did not expect a binary string.



## Tag details

### include

The `!include` tag can be used the short variant, to include a template file using the default renderers:

```yaml
key: !include path/to/template
```

The tag also takes a mapping, which allows specifying more options:

```yaml
key: !include
  # Path to template file
  source: path/to/template

  # Default renderers if not shebang is specified in template file
  default: jinja|yamlet

  # Additional context passed to renderers
  context:
    some_data:
      key: 1
```

### read

The `!read` only supports the show variant and as no options:

```yaml
key: !read path/to/file
```

See [`test/renderers/test_yamlet.py`](https://github.com/jgraichen/salt-tower/blob/main/test/renderers/test_yamlet.py) for more examples and detailed behavior.
