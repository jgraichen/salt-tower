---
title: Introduction
---

# Renderers

Salt-tower ships multiple renderers to ease working with complex pillars and organizaing data.

## Yamlet

The [Yamlet renderer](yamlet.md) is a supercharged YAML renderer that supports including additional files, template or binary files, in a safe and easy manner.

This can help with

* shipping configuration files or snippet, license blobs, private files such as TLS keys, securely from the pillar to minions,

* sharing templates on the master to ship ready to use config files to minions,

* organize and share pillar data between minions,

* working with complex setups, such as multiple customers and brands,

* writing simpler states by just dropping config files blobs instead of thousand lines of JINJA macros.


## Filter

The [filter renderer](filter.md) returns a subset of its data matching grains or pillar keys. This eases organizing data and reusing datasets for multiple minions, roles or any common pillar file.


## Text

The [text renderer](text.md) is a renderer mostly needed in conjunction with the Yamlet renderer when loading and including templates.
