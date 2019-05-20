# Set some defaults for all minions

# A list of all states a minion should execute. The state top file will use
# this list to dynamically render a list. This way there is no need ever update
# the states top file because a minion has been added or changed its role.
#
# See states/top.sls for more information.
#
states:
- salt/minion

# Some default configuration for minion that is written by the
# the salt/minion state.
salt:
  minion:
    hash_type: sha256
    state_output: changes
