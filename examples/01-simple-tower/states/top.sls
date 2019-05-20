base:
#
# Generate dynamic list based on states listed in minions pillar
#
# There is no need to explicitly list any minion or state here. The list
# is compiled from the minion pillar. The top.sls file does not need to be
# updated when a minion is added or changed. Everything is configured on the
# pillar in the `states` list.
#
{% if salt['pillar.get']('states', False) %}
  "{{ grains['id'] }}":
{% for state in salt['pillar.get']('states', []) %}
    - {{ state }}
{% endfor %}
{% endif %}
