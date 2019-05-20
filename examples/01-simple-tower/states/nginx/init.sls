nginx:
  pkg.installed: []
  service.running: []

{% for site in salt['pillar.get']('nginx:sites', {}) %}
/etc/nginx/sites-enabled/{{ site }}:
  file.managed:
    - contents_pillar: nginx:sites:{{ site }}
    - makedirs: True
    - watch_in:
      - service: nginx
    - require_in:
      - service: nginx
{% endfor %}
