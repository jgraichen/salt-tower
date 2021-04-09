# Pillar Data File

Pillar data files define the actual pillar data that is loaded and merged by salt tower. Data files are rendered using the available salt renderers, therefore all usual features are available. The default renderers are `jinja|yamlet`, if no shebang is specified.

## Example

```yaml
include:
  - shared/wordpress

states:
  - nginx
  - php-fpm

nginx:
  package: nginx-light

  sites:
    blog: !include files/nginx.blog.j2
{% if grains["oscodename"] == "bionic" %}
    default: !read files/nginx.default-override.conf
{% endif %}

wordpress:
  config:
    title: Blog for {{ tower.get("site:customer_name") }}
```
