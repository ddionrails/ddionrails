# -*- coding: utf-8 -*-

""" Custom exceptions for ddionrails project """


class Error(Exception):
    """ A base error """

    pass


class DataImportError(Error):
    """ An error to raise when importing data fails """

    pass
