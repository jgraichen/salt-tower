# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
A text renderer for processing and loading text blobs.

It is mainly developed to be used with file loaded in tower pillars and to be
used with the yamlet renderers include tag:

.. code-block:: yaml

    pillar:
      key: !include ./file.txt

.. code-block:: text

    #!text

    The pillar key content.


The following example will render a text file and
strip whitespace from both ends:

.. code-block:: text

    #!text strip

    A short text message


The renderer is further able to wrap the text blob into a nested dictionary:

.. code-block:: text

    #!text strip key=path:to:blob

    A short text message


This will return the following python dict:

.. code-block:: python

    {'path': {'to': {'blob': 'A short text message'}}}

"""


def render(blob, _saltenv, _sls, argline=None, key=None, **_kwargs):
    if not isinstance(blob, str):
        blob = blob.read()

    if blob.startswith("#!"):
        blob = blob[(blob.find("\n") + 1) :]

    if argline is not None:
        for arg in argline.split(None):
            if "=" in arg:
                k, v = arg.split("=", 1)
            else:
                k, v = arg, None

            if k == "strip":
                blob = blob.strip()
            elif k == "key":
                key = v

    if key:
        for k in reversed(key.split(":")):
            blob = {k: blob}

    return blob
