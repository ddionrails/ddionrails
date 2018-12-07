import json
from collections import defaultdict


class ScriptConfig:
    """
    The sub-class has to initialize at least three inputs:

    -   template (string)
    -   fields (list)
    -   default_settings (dict)
    """

    NAME = "abstract-script"

    def __init__(self, script, basket):
        self.basket = basket
        self.script = script

    def get_script_input(self):
        return dict(
            settings=json.loads(self.script.settings),
            data=self.get_datasets_and_variables(),
            template=self.template,
        )

    def get_datasets_and_variables(self):
        datasets = defaultdict(list)
        for variable in self.basket.variables.all():
            dataset_name = variable.dataset.name
            variable_name = variable.name
            datasets[dataset_name].append(variable_name)
        return datasets

    @classmethod
    def get_all_configs(cls):
        return {x.NAME: x for x in cls._get_list_of_configs()}

    @classmethod
    def get_config(cls, config_name):
        return cls.get_all_configs()[config_name]

    @classmethod
    def _get_list_of_configs(cls):
        list_of_configs = cls.__subclasses__()
        for x in cls.__subclasses__():
            list_of_configs += x._get_list_of_configs()
        return list_of_configs


class SoepMixin:

    START_YEAR = 2001

    def _soep_year(self, year):
        letters = self._soep_letters()
        return letters[year - self.START_YEAR]

    def _soep_letters(self, page=None):
        a_num = ord("a")
        g_num = ord("g") + 1
        z_num = ord("z") + 1
        letters1 = [chr(x) for x in range(a_num, z_num)]
        letters2 = ["b" + chr(x) for x in range(a_num, g_num)]
        if page == 1:
            return letters1
        elif page == 2:
            return letters2
        else:
            return letters1 + letters2

    def _soep_classify_dataset(self, dataset_name):
        letters = self._soep_letters()
        h_files = ["%sh" % l for l in letters]
        h_files = h_files + ["%shgen" % l for l in letters]
        h_files = h_files + ["%shost" % l for l in letters]
        h_files = h_files + ["%shausl" % l for l in letters]
        h_files = h_files + ["%shbrutto" % l for l in letters]
        p_files = ["%sp" % l for l in letters]
        p_files = p_files + ["%spgen" % l for l in letters]
        p_files = p_files + ["%spost" % l for l in letters]
        p_files = p_files + ["%spausl" % l for l in letters]
        p_files = p_files + ["%spbrutto" % l for l in letters]
        p_files = p_files + ["%skind" % l for l in letters]
        p_files = p_files + ["%spequiv" % l for l in letters]
        p_files = p_files + ["%spluecke" % l for l in letters]
        p_files = p_files + ["%sppage17" % l for l in letters]
        if dataset_name in h_files:
            return "h"
        elif dataset_name in p_files:
            return "p"
        else:
            return "other"

    def _soep_letter_year(self):
        letter_year = dict()
        letters = self._soep_letters()
        for i in range(len(letters)):
            letter_year[letters[i]] = self.START_YEAR + i
        letter_year[""] = 0
        return letter_year

    def _soep_get_year(self, dataset_name, letters=True):
        if dataset_name[0:2] in self._soep_letters(page=2):
            letter = dataset_name[0:2]
        elif dataset_name[0:1] in self._soep_letters(page=1):
            letter = dataset_name[0:1]
        else:
            letter = ""
        if letters:
            return letter
        else:
            return self._soep_letter_year()[letter]

    def _generate_script_dict(self):
        script_dict = dict()
        for variable in self.basket.variables.all():
            dataset_name = variable.dataset.name
            if not dataset_name in script_dict.keys():
                script_dict[dataset_name] = self._create_dataset_dict(
                    dataset_name, variable
                )
            script_dict[dataset_name]["variables"].add(variable.name)
            for dataset_name, dataset_dict in script_dict.items():
                self._enrich_dataset_dict(dataset_name, dataset_dict)
        return script_dict

    def _create_dataset_dict(self, dataset_name, variable):
        analysis_unit = self._soep_classify_dataset(dataset_name)
        d = dict(
            name=dataset_name,
            analysis_unit=analysis_unit,
            period=self._soep_get_year(dataset_name, letters=False),
            prefix=self._soep_get_year(dataset_name),
            variables=set(),
        )
        return d

    def _enrich_dataset_dict(self, dataset_name, dataset_dict):
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
            d["variables"].add("%shhnr" % d["prefix"])
        else:
            d["matches"] = []
            d["key"] = ""

    def _validate_datasets(self, script_dict, analysis_unit, valid=True):
        valid_list = []
        invalid_list = []
        for dataset_name, dataset_dict in script_dict.items():
            if analysis_unit in dataset_dict["matches"]:
                valid_list.append(dataset_name)
            else:
                invalid_list.append(dataset_name)
            for n in ["phrf", "ppfad"]:
                if n in invalid_list:
                    invalid_list.remove(n)
        if valid:
            return valid_list
        else:
            return invalid_list

    def _get_selected_years(self, script_dict):
        return set([d["prefix"] for d in script_dict.values()])


class SoepStata(ScriptConfig, SoepMixin):

    NAME = "soep-stata"

    COMMENT = "*"

    DEFAULT_DICT = dict(
        path_in="data/",
        path_out="out/",
        analysis_unit="p",
        private="t",
        gender="b",
        balanced="t",
        age_group="adult",
    )
    DEFAULT_CONFIG = json.dumps(DEFAULT_DICT)

    def __init__(self, script, basket):
        self.basket = basket
        self.script = script
        self.fields = [
            dict(name="path_in", label="Input path", scale="text"),
            dict(name="path_out", label="Output path", scale="text"),
            dict(
                name="analysis_unit",
                label="Analysis Unit",
                scale="select",
                options=dict(p="Individual", h="Household"),
            ),
            dict(
                name="private",
                label="Private households",
                scale="select",
                options=dict(t="Private households only", f="All households"),
            ),
            dict(name="gender", label="Gender",
                scale="select", options=dict(
                    b="Both",
                    m="Male",
                    f="Female"),
                ),
            dict(
                name="balanced",
                label="Sample composition",
                scale="select",
                options=dict(t="balanced", f="unbalanced"),
            ),
            dict(
                name="age_group",
                label="Age group",
                scale="select",
                options=dict(
                    all="All sample members",
                    adult="All adult respondents",
                    no17="All adult repspondents without first time interviewed (age 17)",
                ),
            ),
        ]
        self.default_settings = self.DEFAULT_CONFIG
        self.settings = script.get_settings()
        self.template = "scripts/soep_stata.html"
        self.script_dict_raw = self._generate_script_dict()
        valid_datasets = self._validate_datasets(
            self.script_dict_raw, self.settings["analysis_unit"]
        )
        self.script_dict = {
            x: y for x, y in self.script_dict_raw.items() if x in valid_datasets
        }
        self.years = self._get_selected_years(self.script_dict)

    def get_script_input(self):
        script_input = super().get_script_input()
        script_dict = self.script_dict
        script_input["script_dict"] = script_dict
        script_input["years"] = self.years
        script_input["valid_datasets"] = self._validate_datasets(
            self.script_dict_raw, self.settings["analysis_unit"]
        )
        not_processed_datasets = self._validate_datasets(
            self.script_dict_raw, self.settings["analysis_unit"], valid=False
        )
        script_input["not_processed"] = {
            x: y for x, y in script_input["data"].items() if x in not_processed_datasets
        }
        script_input["text"] = "\n".join(
            [
                self._render_disclaimer(),
                self._render_local_variables(),
                self._render_not_processed(script_input["not_processed"]),
                self._render_pfad(),
                self._render_balanced(),
                self._render_private(),
                self._render_gender(),
                self._render_sort_pfad(),
                self._render_hrf(),
                self._render_create_master(),
                self._render_read_data(),
                self._render_merge(),
                self._render_done(),
            ]
        )
        return script_input

    def _render_disclaimer(self):
        script = (
            "\n%s --------------------------------------------------------------------."
            % self.COMMENT
        )
        script += (
            "\n%s This command file was generated by paneldata.org                    ."
            % self.COMMENT
        )
        script += (
            "\n%s --------------------------------------------------------------------."
            % self.COMMENT
        )
        script += (
            "\n%s !!! I M P O R T A N T - W A R N I N G !!!                           ."
            % self.COMMENT
        )
        script += (
            "\n%s You alone are responsible for contents and appropriate.             ."
            % self.COMMENT
        )
        script += (
            "\n%s usage by accepting the usage agreement.                             ."
            % self.COMMENT
        )
        script += (
            "\n%s --------------------------------------------------------------------."
            % self.COMMENT
        )
        script += (
            "\n%s Please report any errors of the code generated here                 ."
            % self.COMMENT
        )
        script += (
            "\n%s to soepmail@diw.de                                                  ."
            % self.COMMENT
        )
        script += (
            "\n%s --------------------------------------------------------------------."
            % self.COMMENT
        )
        script += "\n"
        return script

    def _render_local_variables(self):
        heading = "\n\n* * * LOCAL VARIABLES * * *\n"
        script = '\nglobal MY_PATH_IN   "%s"' % self.settings["path_in"]
        script += '\nglobal MY_PATH_OUT  "%s"' % self.settings["path_out"]
        script += "\nglobal MY_FILE_OUT  ${MY_PATH_OUT}new.dta"
        script += "\nglobal MY_LOG_FILE  ${MY_PATH_OUT}new.log"
        script += "\ncapture log close"
        script += '\nlog using "${MY_LOG_FILE}", text replace'
        script += "\nset more off"
        return heading + script

    def _render_not_processed(self, not_processed):
        heading = "\n\n%s* * * NOT PROCESSED * * *.\n" % self.COMMENT
        script = ""
        for key, value in not_processed.items():
            script += "%s From datasets '%s': %s.\n" % (self.COMMENT, key, value)
        return heading + script

    def _render_pfad(self):
        heading = "\n\n* * * PFAD * * *\n"
        script = []
        if self.settings["analysis_unit"] == "p":
            script.append("\nuse hhnr persnr sex gebjahr psample")
            for y in self.years:
                script.append("%shhnr %snetto %spop" % (y, y, y))
            script.append('using "${MY_PATH_IN}ppfad.dta", clear')
        else:
            script.append("\nuse hhnr hhnrakt hsample")
            for y in self.years:
                script.append("%shhnr %shnetto %shpop" % (y, y, y))
            script.append('using "${MY_PATH_IN}hpfad.dta", clear')
        return heading + " ".join(script)

    def _render_balanced(self):
        heading = "\n\n* * * BALANCED VS UNBALANCED * * *\n"
        connector = "&" if self.settings["balanced"] == "t" else "|"
        if self.settings["analysis_unit"] == "p":
            temp = []
            for y in self.years:
                if self.settings["age_group"] == "adult":
                    temp.append(" (%snetto >= 10 & %snetto < 20) " % (y, y))
                elif self.settings["age_group"] == "no17":
                    temp.append(" (%snetto >= 10 & %snetto < 16) " % (y, y))
                else:
                    temp.append(" (%snetto > 0 & %snetto < 40) " % (y, y))
            return heading + "\nkeep if (" + connector.join(temp) + ")"
        else:
            temp = []
            for y in self.years:
                temp.append(" (%shnetto == 1) " % y)
            return heading + "\nkeep if (" + connector.join(temp) + ")"

    def _render_private(self):
        heading = "\n\n* * * PRIVATE VS ALL HOUSEHOLDS * * *\n"
        set_name = "pop" if self.settings["analysis_unit"] == "p" else "hpop"
        if self.settings["private"] == "t":
            temp = []
            for y in self.years:
                temp.append(" (%s%s == 1 | %s%s == 2) " % (y, set_name, y, set_name))
            return heading + "\nkeep if (" + "|".join(temp) + ")"
        else:
            return heading + "\n/* all households */"
            
    def _render_gender(self):
        heading = "\n\n* * * GENDER ( male = 1 / female = 2) * * *\n"
        if self.settings["gender"] == "m":
            return heading + "\nkeep if (sex == 1)"
        elif self.settings["gender"] == "f":
            return heading + "\nkeep if (sex == 2)"
        else:
            return heading + "\n/* all genders */"

    def _render_sort_pfad(self):
        heading = "\n\n* * * SORT PFAD * * *\n"
        script = ""
        script += '\nsave "${MY_PATH_OUT}pfad.dta", replace'
        return heading + script

    def _render_hrf(self):
        heading = "\n\n* * * HRF * * *\n"
        if self.settings["analysis_unit"] == "p":
            script = '\nuse "${MY_PATH_IN}phrf.dta", clear'
        else:
            script = '\nuse "${MY_PATH_IN}hhrf.dta", clear'
        script += '\nsave "${MY_PATH_OUT}hrf.dta", replace'
        return heading + script

    def _render_create_master(self):
        heading = "\n\n* * * CREATE MASTER * * *\n"
        key = "persnr" if self.settings["analysis_unit"] == "p" else "hhnrakt"
        script = '\nuse "${MY_PATH_OUT}pfad.dta", clear'
        script += (
            '\nmerge 1:1 %s using "${MY_PATH_OUT}hrf.dta", keep(master match) nogen' % key
        )
        script += '\nsave "${MY_PATH_OUT}master.dta", replace'
        return heading + script

    def _render_read_data(self):
        heading = "\n\n* * * READ DATA * * *\n"
        temp = []
        for dataset in self.script_dict.values():
            script = "\nuse %s" % " ".join(dataset["variables"])
            script += ' using "${MY_PATH_IN}%s.dta", clear' % dataset["name"]
            script += '\nsave "${MY_PATH_OUT}%s.dta", replace' % dataset["name"]
            temp.append(script)
        return heading + "\n\n".join(temp)

    def _render_merge(self):
        heading = "\n\n* * * MERGE DATA * * *\n"
        script = '\nuse   "${MY_PATH_OUT}master.dta", clear'
        for dataset in self.script_dict.values():
            if self.settings["analysis_unit"] != dataset["analysis_unit"]:
                merge_factor = "m:1"
            else:
                merge_factor = "1:1"
            script += (
                '\nmerge %s %s using "${MY_PATH_OUT}%s.dta", keep(master match) nogen'
                % (merge_factor, dataset["key"], dataset["name"])
            )
        return heading + script

    def _render_done(self):
        heading = "\n\n* * * DONE * * *\n"
        script = '\nlabel data "paneldata.org: Magic at work!"'
        script += '\nsave "${MY_FILE_OUT}", replace'
        script += "\ndesc"
        script += "\n"
        script += "\nlog close"
        return heading + script


class SoepSpss(SoepStata):

    NAME = "soep-spss"

    def _render_local_variables(self):
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

    def _render_pfad(self):
        script = "\n* ### LOAD [H|P]PFAD ### *.\n"
        if self.settings["analysis_unit"] == "p":
            script += "\nget file = !pathin+'ppfad.sav'"
            script += "\n   /keep = hhnr persnr sex gebjahr psample"
            for y in self.years:
                script += "\n %shhnr %snetto %spop" % (y, y, y)
            script += "."
            script += "\ndataset name ppfad window=asis."
        else:
            script += "\nget file = !pathin+'hpfad.sav'"
            script += "\n   /keep = hhnr hhnrakt hsample"
            for y in self.years:
                script += "\n %shhnr %shnetto %shpop" % (y, y, y)
            script += "."
            script += "\ndataset name hpfad window=asis."
        return script

    def _render_balanced(self):
        heading = "\n* ### [UN]BALANCED ### *.\n"
        connector = "and" if self.settings["balanced"] == "t" else "or"
        temp = []
        if self.settings["analysis_unit"] == "p":
            for y in self.years:
                if self.settings["age_group"] == "adult":
                    temp.append(" (%snetto ge 10 & %snetto lt 20)" % (y, y))
                elif self.settings["age_group"] == "no17":
                    temp.append(" (%snetto ge 10 & %snetto lt 16)" % (y, y))
                else:
                    temp.append(" (%snetto gt 0 & %snetto lt 40)" % (y, y))
            return heading + "\nselect if (" + connector.join(temp) + ")."
        else:
            for y in self.years:
                temp.append(" (%shnetto eq 1)" % y)
            return heading + "\nselect if (" + connector.join(temp) + ")."

    def _render_private(self):
        heading = "\n* ### PRIVATE HOUSEHOLDS ### *.\n"
        set_name = "pop" if self.settings["analysis_unit"] == "p" else "hpop"
        if self.settings["private"] == "t":
            temp = []
            for y in self.years:
                temp.append(" (%s%s eq 1 | %s%s eq 2)" % (y, set_name, y, set_name))
            return heading + "\nselect if (" + "|".join(temp) + ")."
        else:
            return heading + "\n* all households *."
            
    def _render_gender(self):
        heading = "\n* ### GENDER ( male = 1 / female = 2) ### *.\n"
        if self.settings["gender"] == "m":
            return heading + "\nselect if (sex == 1)."
        elif self.settings["gender"] == "f":
            return heading + "\nselect if (sex == 2)."
        else:
            return heading + "\n* all genders *."

    def _render_sort_pfad(self):
        script = "\n* ### SORT [H|P]PFAD ### *.\n"
        if self.settings["analysis_unit"] == "p":
            script += "\nsort cases by persnr."
            script += "\nsave outfile = !pathout+'ppfad.sav'."
        else:
            script += "\nsort cases by hhnrakt."
            script += "\nsave outfile = !pathout+'hpfad.sav'."
        return script

    def _render_hrf(self):
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

    def _render_create_master(self):
        key = "persnr" if self.settings["analysis_unit"] == "p" else "hhnrakt"
        script = "\n* ### CREATE MASTER ### *.\n"
        script += "\nmatch files file  = !pathout+'ppfad.sav'"
        script += "\n           /table = !pathout+'hrf.sav'"
        script += "\n           /by      %s." % key
        script += "\nsort cases by %s." % key
        script += "\nsave outfile = !pathout+'master.sav'."
        return script

    def _render_read_data(self):
        script = "\n* ### READ DATA ### *."
        for dataset in self.script_dict.values():
            script += "\n\nget file = !pathin+'%s.sav'" % dataset["name"]
            script += "\n   /keep = %s." % " ".join(dataset["variables"])
            script += "\ndataset name %s window=asis." % dataset["name"]
            script += "\nsort cases by %s." % dataset["key"]
            script += "\nsave outfile = !pathout+'%s.sav'." % dataset["name"]
        return script

    def _render_merge(self):
        script = "\n* ### MERGE ### *.\n"
        script += "\nget  file = !pathout+'master.sav'."
        script += "\ndataset name master window=asis."
        for dataset in self.script_dict.values():
            script += "\n\nsort cases by %s." % dataset["key"]
            script += "\nmatch files file = *"
            script += "\n          /table = !pathout+'%s.sav'" % dataset["name"]
            script += "\n          /by    = %s." % dataset["key"]
        return script

    def _render_done(self):
        script = "\n* ### DONE ### *.\n"
        script += "\ndataset close all."
        script += "\ndataset name new."
        script += "\ndataset activate new."
        script += '\nfile label "paneldata.org: Magic at work!".'
        script += "\nsave outfile = !pathout+'new.sav'."
        script += "\ndesc all."
        return script


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
            for y in self.years:
                temp.append('"%shhnr", "%snetto", "%spop"' % (y, y, y))
        else:
            script += (
                '\npfad <- read.dta(file.path(path_in, "hpfad.dta"), convert.factors=F)'
            )
            temp = ['"hhnr", "hhnrakt", "hsample"']
            for y in self.years:
                temp.append('"%shhnr", "%shnetto", "%shpop"' % (y, y, y))
        joined = ",".join(temp)
        script += "\npfad <- pfad[ , c(%s)]" % joined
        return script

    def _render_balanced(self):
        heading = "\n### [UN]BALANCED ###\n"
        connector = "&" if self.settings["balanced"] == "t" else "|"
        if self.settings["analysis_unit"] == "p":
            temp = []
            for y in self.years:
                if self.settings["age_group"] == "adult":
                    temp.append(" (%snetto >= 10 & %snetto < 20) " % (y, y))
                elif self.settings["age_group"] == "no17":
                    temp.append(" (%snetto >= 10 & %snetto < 16) " % (y, y))
                else:
                    temp.append(" (%snetto > 0 & %snetto < 40) " % (y, y))
            return heading + "\npfad <- with(pfad, pfad[" + connector.join(temp) + ", ])"
        else:
            temp = []
            for y in self.years:
                temp.append(" (%shnetto == 1) " % y)
            return heading + "\npfad <- with(pfad, pfad[" + connector.join(temp) + ", ])"

    def _render_private(self):
        heading = "\n### PRIVATE HOUSEHOLDS ###\n"
        set_name = "pop" if self.settings["analysis_unit"] == "p" else "hpop"
        if self.settings["private"] == "t":
            temp = []
            for y in self.years:
                temp.append(" (%s%s == 1 | %s%s == 2)" % (y, set_name, y, set_name))
            return heading + "\npfad <- with(pfad, pfad[" + "|".join(temp) + ", ])"
        else:
            return heading + "\n# all households"
            
    def _render_gender(self):
        heading = "\n### GENDER ( male = 1 / female = 2) ###\n"
        if self.settings["gender"] == "m":
            return heading + "\npfad <- pfad[pfad$sex==1,]"
        elif self.settings["gender"] == "f":
            return heading + "\npfad <- pfad[pfad$sex==2,]"
        else:
            return heading + "\n# all genders"

    def _render_sort_pfad(self):
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

    def _render_done(self):
        script = "\n### DONE ###\n"
        script += '\nattr(master, "label") <- "paneldata.org: Magic at work!"'
        script += "\nstr(master)"
        script += '\nsave(master, file=file.path(path_out, "master.RData"))'
        return script

    def _enrich_dataset_dict(self, dataset_name, dataset_dict):
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
