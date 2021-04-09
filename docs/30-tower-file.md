# Tower File

The tower files works similar to the regular `top.sls`. It defines rules which files shall be loaded for a minion, based on e.g. the minion ID, grains, or pillar values.

## Example

```yaml
base:  # salt environment

  # Load common pillar data files for all minions.
  - common/*.sls

  # Use JINJA to load some pillar data files based on
  # some grains, e.g. operating system.
  - dist/{{ grains["oscodename"] }}/*.sls

  # Match a minion by ID
  - "*.example.org":

      # Include a pillar data file for this minion. Path is
      # relative to the tower.sls.
      - roles/example.sls

      # Directly set some pillar values without loading
      # an extra file first.
      - site:
          domain: example.org

  # Match a previously set pillar value
  - "I@site:domain:example.org":
      - site/example/*.sls
```
