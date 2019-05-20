base:
  # Include some common pillar values for all minions.
  #
  # Files matching such a glob are always sorted before being loaded therefore
  # their ordering is deterministic. You can e.g. prefix all files with numbers
  # to ensure their loading order:
  #   10-something.sls
  #   20-else.sls
  #
  - common/*.sls

  # All web minions shall install and setup an nginx web server.
  - 'web*':
    - role/nginx

  # Load minion customizations that can override e.g. role pillar values.
  #
  # The top file will first be render with Jinja, therefore we can insert
  # the current minion ID into the path.
  #
  # See minion/web2/10-nginx-override.sls how a specific minion can override
  # and extend common behavior.
  #
  - minion/{{ minion_id }}/*.sls
