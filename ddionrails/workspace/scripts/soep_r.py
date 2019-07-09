# -*- coding: utf-8 -*-

""" Script generators for ddionrails.workspace app: SoepR """

from .soep_stata import SoepStata


class SoepR(SoepStata):

    NAME = "soep-r"

    COMMENT = "#"

    def _render_local_variables(self):
        script = '\nlibrary("foreign")'
        script += "\n### LOCAL VARIABLES ###"
        script += '\npath_in <- "%s"' % self.settings["path_in"].replace("\\", "/")
        script += '\npath_out <- "%s"' % self.settings["path_out"].replace("\\", "/")
        return script

    def _render_pfad(self):
        script = "\n### LOAD [H|P]PFAD ###\n"
        if self.settings["analysis_unit"] == "p":
            script += (
                '\npfad <- read.dta(file.path(path_in, "ppfad.dta"), convert.factors=F)'
            )
            temp = ['"hhnr", "persnr", "sex", "gebjahr", "psample"']
            for year in self.years:
                temp.append('"%shhnr", "%snetto", "%spop"' % (year, year, year))
        else:
            script += (
                '\npfad <- read.dta(file.path(path_in, "hpfad.dta"), convert.factors=F)'
            )
            temp = ['"hhnr", "hhnrakt", "hsample"']
            for year in self.years:
                temp.append('"%shhnr", "%shnetto", "%shpop"' % (year, year, year))
        joined = ",".join(temp)
        script += "\npfad <- pfad[ , c(%s)]" % joined
        return script

    def _render_balanced(self):
        heading = "\n### [UN]BALANCED ###\n"
        connector = "&" if self.settings["balanced"] == "t" else "|"
        if self.settings["analysis_unit"] == "p":
            temp = []
            for year in self.years:
                if self.settings["age_group"] == "adult":
                    temp.append(" (%snetto >= 10 & %snetto < 20) " % (year, year))
                elif self.settings["age_group"] == "no17":
                    temp.append(" (%snetto >= 10 & %snetto < 16) " % (year, year))
                else:
                    temp.append(" (%snetto > 0 & %snetto < 40) " % (year, year))
            return heading + "\npfad <- with(pfad, pfad[" + connector.join(temp) + ", ])"
        else:
            temp = []
            for year in self.years:
                temp.append(" (%shnetto == 1) " % year)
            return heading + "\npfad <- with(pfad, pfad[" + connector.join(temp) + ", ])"

    def _render_private(self):
        heading = "\n### PRIVATE HOUSEHOLDS ###\n"
        set_name = "pop" if self.settings["analysis_unit"] == "p" else "hpop"
        if self.settings["private"] == "t":
            temp = []
            for year in self.years:
                temp.append(" (%s%s == 1 | %s%s == 2)" % (year, set_name, year, set_name))
            return heading + "\npfad <- with(pfad, pfad[" + "|".join(temp) + ", ])"
        else:
            return heading + "\n# all households"

    def _render_gender(self):
        heading = "\n### GENDER ( male = 1 / female = 2) ###\n"
        gender = self.settings.get("gender", "b")
        if gender == "m":
            return heading + "\npfad <- pfad[pfad$sex==1,]"
        elif gender == "f":
            return heading + "\npfad <- pfad[pfad$sex==2,]"
        else:
            return heading + "\n# all genders"

    @staticmethod
    def _render_sort_pfad():
        script = "\n### SORT [H|P]PFAD ###\n"
        script += "\n# This is R -- no sorting neccessary :-)"
        script += "\n"
        return script

    def _render_hrf(self):
        script = "\n### LOAD [H|P]HRF ###\n"
        if self.settings["analysis_unit"] == "p":
            script += (
                '\nhrf <- read.dta(file.path(path_in, "phrf.dta"), convert.factors=F)'
            )
        else:
            script += (
                '\nhrf <- read.dta(file.path(path_in, "hhrf.dta"), convert.factors=F)'
            )
        return script

    def _render_create_master(self):
        key = "persnr" if self.settings["analysis_unit"] == "p" else "hhnrakt"
        script = "\n### CREATE MASTER ###\n"
        script += '\nmaster <- merge( pfad, hrf, by = "%s")' % key
        return script

    def _render_read_data(self):
        heading = "\n### READ DATA ###\n"
        temp = ["\ndata <- list()"]
        for dataset in self.script_dict.values():
            script = "\ntmp_variables <- c(%s)" % ", ".join(
                ['"%s"' % x for x in dataset["variables"]]
            )
            script += (
                '\ntmp_dataset <- read.dta(file.path(path_in, "%s.dta"), convert.factors=F)'
                % dataset["name"]
            )
            script += '\ndata[["%s"]] <- tmp_dataset[ , tmp_variables]' % dataset["name"]
            temp.append(script)
        return heading + "\n\n".join(temp)

    def _render_merge(self):
        script = "\n### MERGE ###\n"
        for dataset in self.script_dict.values():
            script += (
                '\nmaster <- merge(master, data[["%s"]], by = "%s", all.x=T, all.y=F)'
                % (dataset["name"], dataset["key"])
            )
        return script

    @staticmethod
    def _render_done():
        script = "\n### DONE ###\n"
        script += '\nattr(master, "label") <- "paneldata.org: Magic at work!"'
        script += "\nstr(master)"
        script += '\nsave(master, file=file.path(path_out, "master.RData"))'
        return script

    @staticmethod
    def _enrich_dataset_dict(dataset_dict):
        d = dataset_dict
        analysis_unit = d["analysis_unit"]
        if analysis_unit == "h":
            d["matches"] = ["p", "h"]
            d["key"] = "%shhnr" % d["prefix"]
            d["variables"].add(d["key"])
        elif analysis_unit == "p":
            d["matches"] = ["p"]
            d["key"] = "persnr"
            d["variables"].add(d["key"])
        else:
            d["matches"] = []
            d["key"] = ""
