# Only the web2 minion will service a different www site.
#
# Because we already included `role/nginx` for the minion we do not need to
# declare `states` again. We will just override and extend the configuration.

nginx:
  sites:
    # We can easily reuse an existing template and render it again with
    # different context variables. We could render something else too.
    www: !include
      source: ../../role/files/nginx.www.conf
      context:
        root_path: /var/www/web2

    # Web2 might be some special node and has additional site too:
    web2: !include files/nginx.web2.conf
