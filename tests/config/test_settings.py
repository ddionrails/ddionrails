# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

""" Test cases for settings of ddionrails project """

from importlib import reload


def test_django_debug_settings(monkeypatch):
    monkeypatch.setenv("DJANGO_DEBUG", "True")
    from config.settings import base as settings

    expected = True
    assert expected is settings.DEBUG
    expected = (str(settings.BASE_DIR.joinpath("static")),)
    assert expected == settings.STATICFILES_DIRS
    expected = False
    assert expected is hasattr(settings, "STATIC_ROOT")


def test_django_debug_settings_false(monkeypatch):
    monkeypatch.setenv("DJANGO_DEBUG", "False")
    monkeypatch.setenv("STATIC_ROOT", "static")

    from config.settings import base as settings

    settings = reload(settings)
    expected = False
    assert expected is settings.DEBUG
    expected = "static"
    assert expected == settings.STATIC_ROOT
