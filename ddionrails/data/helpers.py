# -*- coding: utf-8 -*-

""" Helper classes for ddionrails.data app """

import re
from collections import OrderedDict, defaultdict
from typing import Dict, List

from ddionrails.data.models.variable import Variable

LABEL_RE_SOEP = re.compile(r"\s*\[[\w\d\-]*\]\s*")
LABEL_RE_PAIRFAM = re.compile(r"^\s*-*\d*\s*")


class LabelTable:
    """
    Generates a comparison table for the categories of multiple variables.

    Example::

        table = LabelTable([var1, var2, var3])
        table.to_html()
    """

    label_count: int
    label_max: int = 100
    variables: List[Variable]
    variable_max: int = 100

    def __init__(self, variables):
        """Initialize a label table from a list of variables."""

        def sort_helper(variable):
            try:
                period_name = variable.period.name
            except AttributeError:
                period_name = ""
            return period_name

        self.label_count = 0
        self.variable_count = len(variables)

        if len(variables) > self.variable_max:
            self.variables = list()
        else:
            self.variables = sorted(variables, key=sort_helper)

        self.category_labels = self._get_all_category_labels()

    @property
    def render_table(self) -> bool:
        """Determine if Table should be rendered in html."""
        if not self.variables:
            return False
        if self.label_count > self.label_max:
            return False
        return True

    def to_dict(self):
        """
        Returns the label table as a dict.
        """
        table = dict(header=[], body=OrderedDict())
        self._fill_header(table)
        self._fill_body(table)
        return table

    def to_html(self):
        """Create a string representing the table as html table."""
        if not self.render_table:
            return ""
        label_dict = self.to_dict()
        try:
            label_dict = self.to_dict()
        except:
            pass
        result = [
            '<table class="table" id="label_table">',
            "<thead><tr>",
            '<th><i class="fa fa-chart-bar" title="Variable"></i> Variable</th>',
        ]
        try:
            for var in label_dict["header"]:
                result.append('<th><a href="%s">%s</a></th>' % (str(var), var.name))
            result.append(
                '</tr><tr><th><i class="fa fa-table" title="Dataset"></i> Dataset</th>'
            )
            for var in label_dict["header"]:
                dat = var.dataset
                result.append('<th><a href="%s">%s</a></th>' % (str(dat), dat.name))
            result.append("</tr></thead><tbody>")
            for val, variables in label_dict["body"].items():
                result.append("<tr>")
                result.append("<th>%s</th>" % val)
                for var in variables:
                    if var:
                        result.append(
                            "<td>%s (%s)</td>" % (var["value"], var["frequency"])
                        )
                    else:
                        result.append("<td></td>")
                result.append("</tr>")
            result.append("</tbody></table>")
        except:
            pass
        return "\n".join(result)

    def _fill_header(self, table):
        for variable in self.variables:
            table["header"].append(variable)

    def _fill_body(self, table):
        for category_label in self.category_labels:
            row = list()
            for variable in self.variables:
                try:
                    category = [
                        c
                        for c in variable.get_categories()
                        if self._simplify_label(c["label"]) == category_label
                    ][0]
                    row.append(
                        dict(value=category["value"], frequency=category["frequency"])
                    )
                except:
                    row.append(None)
            table["body"][category_label] = row

    def _get_all_category_labels(self) -> Dict[str, List[str]]:
        labels: Dict[str, List[str]] = defaultdict(list)
        for variable in self.variables:
            for category in variable.get_categories():
                labels[self._simplify_label(category["label"])].append(category["value"])
            if len(labels) > self.label_max:
                self.label_count = len(labels)
                return dict()

        def sort_helper(elements):
            temp_list = list()
            for element in elements[1]:
                if element and element != "":
                    try:
                        temp_list.append(int(element))
                    # afuetterer: the int(x) might fail,
                    # when x is cannot be cast to an integer?
                    except ValueError:
                        pass
            try:
                return sum(temp_list) / len(temp_list)
            # afuetterer: the temp_list might be empty?
            except ZeroDivisionError:
                return 100000000

        labels = sorted(list(labels.items()), key=sort_helper)
        labels = [category[0] for category in labels]
        return labels

    @staticmethod
    def _simplify_label(label):
        label = str(label)
        label = label.lower().strip()
        label = LABEL_RE_SOEP.sub("", label)
        label = LABEL_RE_PAIRFAM.sub("", label)
        return label
