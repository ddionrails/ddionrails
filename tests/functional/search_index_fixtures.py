from types import MappingProxyType

from django.core.management import call_command
from django.db.models import QuerySet
from django.test import override_settings
from elasticsearch import RequestError

from ddionrails.concepts.documents import ConceptDocument, TopicDocument
from ddionrails.data.documents import VariableDocument
from ddionrails.instruments.documents import QuestionDocument
from ddionrails.publications.documents import PublicationDocument

model_type_document_mapper = MappingProxyType(
    {
        "concepts": ConceptDocument,
        "publications": PublicationDocument,
        "questions": QuestionDocument,
        "topics": TopicDocument,
        "variables": VariableDocument,
    }
)

@override_settings(ELASTICSEARCH_DSL_AUTOSYNC=True)
def set_up_index(test_case, model_object, model_type_plural):
    document = model_type_document_mapper[model_type_plural]

    document._index._name = f"testing_{model_type_plural}"
    if document._index.exists():
        document._index.delete()
    document._index.create()
    expected = 1
    if isinstance(model_object, QuerySet):
        expected = model_object.count()
        for _object in model_object:
            _object.save()
    else:
        model_object.save()
    try:
        call_command("search_index", "--create", "--no-parallel", force=True)
    except RequestError:
        pass

    # Run tests

    test_case.assertEqual(expected, document.search().count())
    

    # Run test
    return document

def tear_down_index(test_case, model_type_plural):
    document = model_type_document_mapper[model_type_plural]
    document._index._name = f"testing_{model_type_plural}"
    response = document.search().query("match_all").delete()
    test_case.assertGreater(response["deleted"], 0)
    document._index.delete()
