# -*- coding: utf-8 -*-

""" Views for ddionrails.workspace app """

from .basket import (
    add_concept,
    add_variable,
    basket_delete,
    basket_detail,
    basket_list,
    basket_new,
    basket_search,
    basket_to_csv,
    remove_concept,
    remove_variable,
)
from .script import script_delete, script_detail, script_new_lang, script_raw
from .user import account_overview, register, user_delete
