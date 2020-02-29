# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import textwrap

import pytest


@pytest.fixture
def result(env):
    def fn():
        return env.compile_template('template.sls', default='text')

    return fn


def test_render(env, result):
    env.write('template.sls', 'A small text')

    assert result() == 'A small text'


def test_strip(env, result):
    env.write('template.sls', textwrap.dedent(
        '''
        #!text strip

            Indented text

        END

        '''
        ).lstrip())

    assert result() == 'Indented text\n\nEND'


def test_key(env, result):
    env.write('template.sls', textwrap.dedent(
        '''
        #!text key=a:b:c
        text value
        '''
        ).strip())

    assert result() == {'a': {'b': {'c': 'text value'}}}
