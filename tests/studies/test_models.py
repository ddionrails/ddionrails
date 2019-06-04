import pathlib

import pytest

from ddionrails.studies.models import Study, context

pytestmark = [pytest.mark.studies, pytest.mark.models]


class TestStudyModel:
    def test_string_method(self, study):
        assert str(study) == "/" + study.name

    def test_get_absolute_url_method(self, study):
        assert study.get_absolute_url() == "/" + study.name

    def test_import_path_method(self, study, settings):
        expected = (
            str(
                pathlib.Path(settings.IMPORT_REPO_PATH)
                / study.name
                / settings.IMPORT_SUB_DIRECTORY
            )
            + "/"
        )
        assert study.import_path() == expected

    def test_repo_url_method_https(self, study, settings):
        settings.GIT_PROTOCOL = "https"
        repo_url = study.repo_url()
        assert repo_url.startswith("https")
        assert study.repo in repo_url

    def test_repo_url_method_ssh(self, study, settings):
        settings.GIT_PROTOCOL = "ssh"
        repo_url = study.repo_url()
        assert repo_url.startswith("git")
        assert study.repo in repo_url

    def test_repo_url_method_exception(self, study, settings):
        settings.GIT_PROTOCOL = None
        with pytest.raises(Exception) as excinfo:
            study.repo_url()
            assert excinfo.value == "Specify a protocol for Git in your settings."

    def test_has_topics_method(self, study):
        assert False is study.has_topics()

    def test_has_topics_method_returns_true(self, study):
        study.topic_languages = ["en"]
        study.save()
        assert True is study.has_topics()


def test_context_function_with_study(study, rf):
    some_request = rf.get("/")
    response = context(some_request)
    queryset = Study.objects.filter(id=study.id)
    assert str(response) == str({"all_studies": queryset})


def test_context_function_without_study(rf, db):
    some_request = rf.get("/")
    response = context(some_request)
    empty_queryset = Study.objects.none()
    assert str(response) == str({"all_studies": empty_queryset})
