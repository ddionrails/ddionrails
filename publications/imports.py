import bibtexparser

from imports import imports

from .forms import PublicationForm
from .models import Publication


class PublicationImport(imports.Import):
    def execute_import(self):
        bibtex = bibtexparser.loads(self.content)
        self.bibtex = bibtex
        for item in bibtex.entries:
            try:
                self._import_publication(item)
            except:
                print("X")

    def _import_publication(self, bibtex_item):
        label = "%s (%s): %s" % (
            bibtex_item.get("author", ""),
            bibtex_item.get("year", ""),
            bibtex_item.get("title", ""),
        )
        bibtex_item["namespace"] = self.study.name
        bibtex_item["study"] = self.study.name
        bibtex_item["label"] = label
        bibtex_item["period"] = bibtex_item.get("year", "")
        import_dict = dict(name=bibtex_item["ID"], study=self.study.id, label=label)
        try:
            name = PublicationForm(import_dict).data["name"]
            x = Publication.objects.get(name=name)
        except:
            x = None
        form = PublicationForm(import_dict, instance=x)
        form.full_clean()
        if form.is_valid():
            publication = form.save()
            publication.set_elastic(bibtex_item)
            print("p", end="")
        else:
            print("\n[ERROR] Broken publication import", form.data)
