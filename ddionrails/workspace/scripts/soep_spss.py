# -*- coding: utf-8 -*-

""" Script generators for ddionrails.workspace app: SoepSpss """

from .soep_stata import SoepStata


class SoepSpss(SoepStata):
    """ Script Generator for SPSS scripts """

    NAME = "soep-spss"

    def _render_local_variables(self) -> str:
        """ Render a "local variables" section of the script file """
        script = "\nset compression on."
        script += "\nset header off."
        script += "\n"
        script += "\ndataset close all."
        script += "\n"
        script += "\n"
        script += "\n* ### LOCAL VARIABLES ### *."
        script += "\n"
        script += '\ndefine !pathin() "%s" !enddefine.' % self.settings["path_in"]
        script += '\ndefine !pathout() "%s" !enddefine.' % self.settings["path_out"]
        return script

    def _render_pfad(self) -> str:
        """ Render a "load pfad" section of the script file """
        script = "\n* ### LOAD [H|P]PFAD ### *.\n"
        if self.settings["analysis_unit"] == "p":
            script += "\nget file = !pathin+'ppfad.sav'"
            script += "\n   /keep = hhnr persnr sex gebjahr psample"
            for year in self.years:
                script += "\n %shhnr %snetto %spop" % (year, year, year)
            script += "."
            script += "\ndataset name ppfad window=asis."
        else:
            script += "\nget file = !pathin+'hpfad.sav'"
            script += "\n   /keep = hhnr hhnrakt hsample"
            for year in self.years:
                script += "\n %shhnr %shnetto %shpop" % (year, year, year)
            script += "."
            script += "\ndataset name hpfad window=asis."
        return script

    def _render_balanced(self) -> str:
        """ Render a "balanced" section of the script file """
        heading = "\n* ### [UN]BALANCED ### *.\n"
        connector = "and" if self.settings["balanced"] == "t" else "or"
        temp = []
        if self.settings["analysis_unit"] == "p":
            for year in self.years:
                if self.settings["age_group"] == "adult":
                    temp.append(" (%snetto ge 10 & %snetto lt 20)" % (year, year))
                elif self.settings["age_group"] == "no17":
                    temp.append(" (%snetto ge 10 & %snetto lt 16)" % (year, year))
                else:
                    temp.append(" (%snetto gt 0 & %snetto lt 40)" % (year, year))
            return heading + "\nselect if (" + connector.join(temp) + ")."
        else:
            for year in self.years:
                temp.append(" (%shnetto eq 1)" % year)
            return heading + "\nselect if (" + connector.join(temp) + ")."

    def _render_private(self) -> str:
        """ Render a "private households" section of the script file """
        heading = "\n* ### PRIVATE HOUSEHOLDS ### *.\n"
        set_name = "pop" if self.settings["analysis_unit"] == "p" else "hpop"
        if self.settings["private"] == "t":
            temp = []
            for year in self.years:
                temp.append(" (%s%s eq 1 | %s%s eq 2)" % (year, set_name, year, set_name))
            return heading + "\nselect if (" + "|".join(temp) + ")."
        else:
            return heading + "\n* all households *."

    def _render_gender(self) -> str:
        """ Render a "gender" section of the script file """
        heading = "\n* ### GENDER ( male = 1 / female = 2) ### *.\n"
        gender = self.settings.get("gender", "b")
        if gender == "m":
            return heading + "\nselect if (sex == 1)."
        elif gender == "f":
            return heading + "\nselect if (sex == 2)."
        else:
            return heading + "\n* all genders *."

    def _render_sort_pfad(self) -> str:
        """ Render a "sort pfad" section of the script file """
        script = "\n* ### SORT [H|P]PFAD ### *.\n"
        if self.settings["analysis_unit"] == "p":
            script += "\nsort cases by persnr."
            script += "\nsave outfile = !pathout+'ppfad.sav'."
        else:
            script += "\nsort cases by hhnrakt."
            script += "\nsave outfile = !pathout+'hpfad.sav'."
        return script

    def _render_hrf(self) -> str:
        """ Render a "load hrf" section of the script file """
        script = "\n* ### LOAD [H|P]HRF ### *.\n"
        if self.settings["analysis_unit"] == "p":
            script += "\nget file !pathin+'phrf.sav'."
            script += "\ndataset name phrf window=asis."
            script += "\nsort cases by persnr."
        else:
            script += "\nget file !pathin+'hhrf.sav'."
            script += "\ndataset name hhrf window=asis."
            script += "\nsort cases by hhnrakt."
        script += "\nsave outfile = !pathout+'hrf.sav'."
        return script

    def _render_create_master(self) -> str:
        """ Render a "create master" section of the script file """
        key = "persnr" if self.settings["analysis_unit"] == "p" else "hhnrakt"
        script = "\n* ### CREATE MASTER ### *.\n"
        script += "\nmatch files file  = !pathout+'ppfad.sav'"
        script += "\n           /table = !pathout+'hrf.sav'"
        script += "\n           /by      %s." % key
        script += "\nsort cases by %s." % key
        script += "\nsave outfile = !pathout+'master.sav'."
        return script

    def _render_read_data(self) -> str:
        """ Render a "read data" section of the script file """
        script = "\n* ### READ DATA ### *."
        for dataset in self.script_dict.values():
            script += "\n\nget file = !pathin+'%s.sav'" % dataset["name"]
            script += "\n   /keep = %s." % " ".join(dataset["variables"])
            script += "\ndataset name %s window=asis." % dataset["name"]
            script += "\nsort cases by %s." % dataset["key"]
            script += "\nsave outfile = !pathout+'%s.sav'." % dataset["name"]
        return script

    def _render_merge(self) -> str:
        """ Render a "merge" section of the script file """
        script = "\n* ### MERGE ### *.\n"
        script += "\nget  file = !pathout+'master.sav'."
        script += "\ndataset name master window=asis."
        for dataset in self.script_dict.values():
            script += "\n\nsort cases by %s." % dataset["key"]
            script += "\nmatch files file = *"
            script += "\n          /table = !pathout+'%s.sav'" % dataset["name"]
            script += "\n          /by    = %s." % dataset["key"]
        return script

    @staticmethod
    def _render_done() -> str:
        """ Render a "done" section of the script file """
        return (
            "\n"
            "* ### DONE ### *.\n\n"
            "dataset close all.\n"
            "dataset name new.\n"
            "dataset activate new.\n"
            'file label "paneldata.org".\n'
            "save outfile = !pathout+'new.sav'.\n"
            "desc all."
        )
