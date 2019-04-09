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

    # def test_get_list_of_topic_files_method_without_files(self, study, mocker):
    #     mocker.patch("glob.glob", return_value=["topic1.md"])
    #     topics = study.get_list_of_topic_files()
    #     assert topics == ["topic1.md"]
    #
    # def test_has_topics_method_with_topic_files(self, study, mocker):
    #     mocker.patch("studies.models.Study.get_list_of_topic_files", return_value=["topic1.md"])
    #     assert study.has_topics() is True
    #
    # def test_has_topics_method_without_topic_files(self, study, mocker):
    #     mocker.patch("studies.models.Study.get_list_of_topic_files", return_value=[])
    #     assert study.has_topics() is False

    def test_get_config_method_text(self, study):
        study.config = '{"some-key": "some-value"}'
        config = study.get_config(text=True)
        assert config == study.config
        assert isinstance(config, str)

    def test_get_config_method_json_success(self, study):
        study.config = '{"some-key": "some-value"}'
        config = study.get_config(text=False)
        assert config == {"some-key": "some-value"}

    def test_get_config_method_json_failure(self, study):
        config = study.get_config(text=False)
        assert config == []


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
