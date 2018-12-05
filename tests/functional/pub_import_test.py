#!/usr/bin/env python

from publications.imports import PublicationImport
from studies.models import Study

def run():
    print("hi")
    s = Study.objects.first()
    PublicationImport.run_import(
        "bibtex.bib",
        study = s,
    )
    print("hi")

if __name__ == "__main__":
    run()
