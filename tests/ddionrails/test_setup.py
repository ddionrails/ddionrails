from ddionrails.setup import setup


def test_setup(mocker):
    mocked_django_setup = mocker.patch("django.setup")
    setup()
    mocked_django_setup.assert_called_once()
