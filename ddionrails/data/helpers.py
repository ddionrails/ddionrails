# -*- coding: utf-8 -*-

""" Helper classes for ddionrails.data app """

import re
from collections import OrderedDict, defaultdict

LABEL_RE_SOEP = re.compile(r"\s*\[[\w\d\-]*\]\s*")
LABEL_RE_PAIRFAM = re.compile(r"^\s*-*\d*\s*")


class LabelTable:
    """
    Generates a comparison table for the categories of multiple variables.

    Example::

        table = LabelTable([var1, var2, var3])
        table.to_html()
    """

    def __init__(self, variables):
        """
        Initialize a label table from a list of variables.
        """

        def sort_helper(variable):
            try:
                x = variable.dataset.period.name
            except AttributeError:
                x = ""
            return x

        self.variables = sorted(variables, key=sort_helper)

    def to_dict(self):
        """
        Returns the label table as a dict.
        """
        t = dict(header=[], body=OrderedDict())
        self._fill_header(t)
        self._fill_body(t)
        return t

    def to_html(self):
        try:
            label_dict = self.to_dict()
        except:
            pass
        result = [
            '<table class="table" id="label_table">',
            "<thead><tr>",
            "<th>Variable:</th>",
        ]
        try:
            for var in label_dict["header"]:
                result.append('<th><a href="%s">%s</a></th>' % (str(var), var.name))
            result.append("</tr><tr><th>Dataset:</th>")
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

    def _fill_header(self, t):
        for variable in self.variables:
            t["header"].append(variable)

    def _fill_body(self, t):
        for category_label in self._get_all_category_labels():
            x = []
            for variable in self.variables:
                try:
                    category = [
                        c
                        for c in variable.get_categories()
                        if self._simplify_label(c["label"]) == category_label
                    ][0]
                    x.append(
                        dict(value=category["value"], frequency=category["frequency"])
                    )
                except:
                    x.append(None)
            t["body"][category_label] = x

    def _get_all_category_labels(self):
        categories = defaultdict(list)
        for variable in self.variables:
            for category in variable.get_categories():
                categories[self._simplify_label(category["label"])].append(
                    category["value"]
                )

        def sort_helper(x):
            temp_list = []
            for x in x[1]:
                if x and x != "":
                    try:
                        temp_list.append(int(x))
                    except:
                        pass
            try:
                return sum(temp_list) / len(temp_list)
            except:
                return 100000000

        categories = sorted(list(categories.items()), key=sort_helper)
        categories = [x[0] for x in categories]
        return categories

    @staticmethod
    def _simplify_label(label):
        try:
            label = label.lower().strip()
            label = LABEL_RE_SOEP.sub("", label)
            label = LABEL_RE_PAIRFAM.sub("", label)
            return label
        except:
            return ""
