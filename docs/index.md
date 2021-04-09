---
title: Welcome
---

# Salt Tower — A Flexible External Pillar Module

[![GitHub Workflow Status (master branch)](https://img.shields.io/github/workflow/status/jgraichen/salt-tower/Python%20Package/master?logo=github)](https://github.com/jgraichen/salt-tower/actions?query=branch%3Amaster+workflow%3A%22Python+Package%22)

Salt Tower is an advanced and flexible external pillar module that gives access to pillar values while processing and merging them, can render all usual salt file formats and include private and binary files for a minion.

Salt Tower is inspired by [pillarstack](https://github.com/bbinet/pillarstack) for merging pillar files and giving access to them. It also has a top file like salt itself and utilizes salt renderers to supports all formats such as YAML, JINJA, Python and any combination. Supercharged [renderers for plain text and YAML](renderers/index.md) are included too.

Each tower data file is passed the current processed pillars. They can therefore access previously defined values. Data files can include other files that are all merged together.

Salt Tower is designed to completely replace the usual pillar repository or can be utilized beside salts original pillar that e.g. can bootstrap a salt master with Salt Tower.
