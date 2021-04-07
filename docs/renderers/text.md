# Text

The `text` renderer converts an input into a string. This is needed to e.g. embed the result from the JINJA renderer into a text string, to be embedded into the pillar.

The renderer further has options to strip leading and trailing whitespace.

!!! note

    Read more about salts rendering pipeline and how to combine renderers in the [official documentation](https://docs.saltproject.io/en/master/ref/renderers/index.html).

## Example

### Strip whitespace

```jinja
#!jinja|text strip

# role/webserver/files/nginx.default.j2
# We want this file to be rendered using JINJA first, and into
# a text string second, to be included as a string in the pillar.

server {
    listen 80 default_server;
    server_name {{ grains['localhost'] }};

    root /var/www/html;
}


(Some newlines here)
```

This will render the template with JINJA and return the result as a text string. Leading and trailing whitespace will be stripped.

```
# role/webserver/files/nginx.default.j2
# We want this file to be rendered using JINJA first, and into
# a text string second, to be included as a string in the pillar.

server {
    listen 80 default_server;
    server_name the-machine-hostname;

    root /var/www/html;
}
```

### Nest text inside a dictionary

In same case it might be needed or easier to have the renderer return the text in a (nested) dictionary, e.g. to be merged correctly into a specific pillar data file. The optional `key` arguments allows to give a "path" to nested the text inside a dict:

```
#!text key=nginx:site:default

server {
    listen 80;
    root /var/www/html;
}
```

This will return the file as the following data structure:

```yaml
nginx:
  site:
    default: |
      server {
          listen 80;
          root /var/www/html;
      }
```

## Arguments

`strip`
: Removes leading and trailing whitespace.

`key=a:b:c`
: Nests the text string in a (nested) dictionary at the given path.

See [`test/renderers/test_text.py`](https://github.com/jgraichen/salt-tower/blob/main/test/renderers/test_text.py) for more examples and detailed behavior.
