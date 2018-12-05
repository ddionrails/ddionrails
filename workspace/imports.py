from imports import imports

from .forms import BasketCSVForm, BasketVariableForm, UserForm


class BasketImport(imports.CSVImport):
    class DOR:
        form = BasketCSVForm


class BasketVariableImport(imports.CSVImport):
    class DOR:
        form = BasketVariableForm


class UserImport(imports.CSVImport):
    class DOR:
        form = UserForm
