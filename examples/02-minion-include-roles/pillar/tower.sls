base:
  # Load minion pillar by ID.
  #
  # Easy when handling limited number of minions. Each minion data file will
  # include needs roles itself.
  #
  - minion/{{ minion_id }}/*.sls
