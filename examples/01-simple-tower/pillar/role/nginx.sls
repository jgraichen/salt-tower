# Nginx minions need to execute the nginx state
states:
- nginx

# Nginx shall be configured with two sites that are shipped as plain
# configuration file blobs based on custom templates. These templates are
# rendered from the pillar on the salt master and are completely independent
# of the state.
nginx:
  sites:
    # The yamlet render can render and included templates from the pillar
    # as a text blob in the pillar. We can use Jinja or anything else supported
    # by salt in the template.
    #
    # The rendered template will be inserted as a string by the YAML parser
    # itself without any formatting or encoding issue.
    default: !include files/nginx.default.conf

    # We can reuse templates between minions or roles by passing custom
    # context variables right from the pillar. The template can
    # share what it needs, adjusted and customized without having
    # to adjust any state.
    #
    # Just use the !include macro with arguments:
    www: !include
      source: files/nginx.www.conf
      context:
        root_path: /var/www/public
