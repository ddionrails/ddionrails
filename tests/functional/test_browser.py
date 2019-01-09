import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from tests.factories import UserFactory
from tests.workspace.test_forms import valid_basket_data

pytestmark = [pytest.mark.functional]


@pytest.fixture()
def authenticated_browser(selenium, client, live_server, known_user):
    """Return a browser instance with logged-in user session."""
    # https://flowfx.de/blog/test-django-with-selenium-pytest-and-user-authentication/
    client.login(username=known_user.username, password="secret")
    cookie = client.cookies["sessionid"]
    selenium.get(live_server.url)
    selenium.add_cookie(
        {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
    )
    # selenium.refresh()
    return selenium


# @pytest.mark.skip(reason="no way of currently testing this")
class TestNavigation:
    def test_home_page(self, selenium, live_server):
        selenium.get(live_server.url)
        assert selenium.title == "paneldata.org"

    def test_get_contact_page_from_home(self, selenium, live_server):
        selenium.get(live_server.url)
        contact_link = selenium.find_element_by_link_text("Contact / feedback")
        contact_link.click()
        heading = selenium.find_element_by_tag_name("h1")
        assert heading.text == "Contact / feedback"
        assert "SOEP Hotline" in selenium.page_source
        assert "GitHub" in selenium.page_source

    def test_get_imprint_page_from_home(self, selenium, live_server):
        selenium.get(live_server.url)
        imprint_link = selenium.find_element_by_link_text("Imprint")
        imprint_link.click()
        heading = selenium.find_element_by_tag_name("h1")
        assert heading.text == "Imprint"
        assert "SOEP" in selenium.page_source
        assert "Fratzscher" in selenium.page_source
        assert "Liebig" in selenium.page_source
        assert "Berlin" in selenium.page_source
        assert "Privacy policy at DIW Berlin" in selenium.page_source

    def test_get_back_home_from_other_page(self, selenium, live_server):
        selenium.get(live_server.url + "/search/")
        home_link = selenium.find_element_by_link_text("paneldata.org")
        home_link.click()
        assert selenium.title == "paneldata.org"

    def test_get_search_page_from_home(self, selenium, live_server):
        selenium.get(live_server.url)
        search_link = selenium.find_element_by_link_text("Search")
        search_link.click()
        assert "Keep my filters" in selenium.page_source

    def test_get_login_page_from_home(self, selenium, live_server):
        selenium.get(live_server.url)
        login_link = selenium.find_element_by_link_text("Register / log in")
        login_link.click()
        assert "User login" in selenium.page_source

    def test_get_register_page_from_login(self, selenium, live_server):
        selenium.get(live_server.url + "/workspace/login/")
        register_link = selenium.find_element_by_xpath("//a[contains(@href,'register')]")
        register_link.click()
        assert "User registration" in selenium.page_source

    def test_get_password_reset_page_from_login(self, selenium, live_server):
        selenium.get(live_server.url + "/workspace/login/")
        password_reset_link = selenium.find_element_by_xpath(
            "//a[contains(@href,'password_reset')]"
        )
        password_reset_link.click()
        heading = selenium.find_element_by_tag_name("h1")
        assert heading.text == "Django administration"
        assert "Forgotten your password?" in selenium.page_source

    def test_studies_dropdown_menu(self, selenium, live_server, study):
        selenium.get(live_server.url)
        studies_dropdown_menu = selenium.find_element_by_xpath(
            '//button[contains(text(), "Studies")]'
        )
        expanded = studies_dropdown_menu.get_attribute("aria-expanded")
        assert expanded == "false"
        studies_dropdown_menu.click()
        expanded = studies_dropdown_menu.get_attribute("aria-expanded")
        assert expanded == "true"

    def test_study_link_from_dropdown_menu(self, selenium, live_server, study):
        selenium.get(live_server.url)
        study_list = selenium.find_element_by_css_selector("div.list-group")
        study_link = study_list.find_element_by_link_text(study.label)
        study_link.click()
        study_info_box = selenium.find_element_by_css_selector("div.panel-body")
        assert study.name in study_info_box.text
        assert study.label in study_info_box.text

    def test_study_link_from_home_page_list(self, selenium, live_server, study):
        selenium.get(live_server.url)
        study_list = selenium.find_element_by_css_selector("div.list-group")
        study_link = study_list.find_element_by_link_text(study.label)
        study_link.click()
        study_info_box = selenium.find_element_by_css_selector("div.panel-body")
        assert study.name in study_info_box.text
        assert study.label in study_info_box.text

    def test_study_page(self, selenium, live_server, study):
        selenium.get(live_server.url + "/" + study.name)
        study_nav_bar = selenium.find_element_by_id("navbar")
        assert study_nav_bar.find_element_by_link_text("Data")
        assert study_nav_bar.find_element_by_link_text("Instruments")
        assert study_nav_bar.find_element_by_link_text("Publications")

    def test_study_datasets_section_link(self, selenium, live_server, study, dataset):
        dataset.study = study
        selenium.get(live_server.url + "/" + study.name)
        study_nav_bar = selenium.find_element_by_id("navbar")
        datasets_section_link = study_nav_bar.find_element_by_link_text("Data")
        datasets_section_link.click()

        dataset_table = selenium.find_element_by_id("dataset_table_wrapper")
        dataset_link = dataset_table.find_element_by_link_text(dataset.name)
        assert dataset_link

    def test_study_instruments_section_link(
        self, selenium, live_server, study, instrument
    ):
        instrument.study = study
        selenium.get(live_server.url + "/" + study.name)
        study_nav_bar = selenium.find_element_by_id("navbar")
        instruments_section_link = study_nav_bar.find_element_by_link_text("Instruments")
        instruments_section_link.click()

        instrument_table = selenium.find_element_by_id("instrument_table_wrapper")
        instrument_link = instrument_table.find_element_by_link_text(instrument.name)
        assert instrument_link

    def test_study_publications_link(self, selenium, live_server, study):
        pass

    # TODO
    # datatable search


@pytest.mark.skip(reason="no way of currently testing this")
class TestDatasetPage:
    def test_dataset_page(self, selenium, live_server, study, dataset, variable):
        dataset.study = study
        variable.dataset = dataset
        selenium.get(live_server.url + dataset.get_absolute_url())


class TestVariablePage:
    pass
    # http://localhost:8000/soep-test/data/ah/hid


class TestInstrumentPage:
    pass
    # http://localhost:8000/soep-test/inst/soep-test-2011-ah


class TestQuestionPage:
    pass
    # http://localhost:8000/soep-test/inst/soep-test-2011-ah/income


class TestPublicationPage:
    pass
    # http://localhost:8000/soep-test/publ/soeplit7691


@pytest.fixture
def known_user():
    return UserFactory(username="knut", password="secret")


# @pytest.mark.skip(reason="no way of currently testing this")
class TestWorkspace:

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_login_with_known_user(self, selenium, live_server, known_user):
        selenium.get(live_server.url + "/workspace/login/")
        input_user_name = selenium.find_element_by_id("id_username")
        input_password = selenium.find_element_by_id("id_password")
        input_user_name.send_keys("knut")
        input_password.send_keys("secret")
        login_button = selenium.find_element_by_xpath('//input[@value="Login"]')
        login_button.click()
        baskets_link = selenium.find_element_by_link_text("My baskets")
        assert baskets_link
        account_link = selenium.find_element_by_link_text("My account")
        assert account_link
        logout_link = selenium.find_element_by_link_text("Logout")
        assert logout_link

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_logout_with_known_user(self, selenium, live_server, known_user):
        selenium.get(live_server.url + "/workspace/login/")
        input_user_name = selenium.find_element_by_id("id_username")
        input_password = selenium.find_element_by_id("id_password")
        input_user_name.send_keys("knut")
        input_password.send_keys("secret")
        login_button = selenium.find_element_by_xpath('//input[@value="Login"]')
        login_button.click()
        logout_link = selenium.find_element_by_link_text("Logout")
        logout_link.click()

        with pytest.raises(NoSuchElementException):
            selenium.find_element_by_link_text("My baskets")

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_register_user(self, selenium, live_server):
        selenium.get(live_server.url + "/workspace/register/")
        input_user_name = selenium.find_element_by_id("id_username")
        input_password1 = selenium.find_element_by_id("id_password1")
        input_password2 = selenium.find_element_by_id("id_password2")
        input_user_name.send_keys("knut")
        input_password1.send_keys("secret")
        input_password2.send_keys("secret")
        register_button = selenium.find_element_by_xpath('//input[@value="Register"]')
        register_button.click()

        # TODO: Redirect?

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_login_with_unknown_user(self, selenium, live_server):
        selenium.get(live_server.url + "/workspace/login/")
        input_user_name = selenium.find_element_by_id("id_username")
        input_password = selenium.find_element_by_id("id_password")

        input_user_name.send_keys("unkown")
        input_password.send_keys("secret")
        login_button = selenium.find_element_by_xpath('//input[@value="Login"]')
        login_button.click()
        assert (
            "Please enter a correct username and password. "
            "Note that both fields may be case-sensitive."
            in selenium.page_source
        )

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_baskets_page(self, authenticated_browser, live_server):
        authenticated_browser.get(live_server.url + "/workspace/login/")
        baskets_link = authenticated_browser.find_element_by_link_text("My baskets")
        baskets_link.click()
        heading = authenticated_browser.find_element_by_tag_name("h1")
        assert heading.text == "Baskets"

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_create_basket(self, authenticated_browser, live_server, study):
        authenticated_browser.get(live_server.url + "/workspace/login/")
        baskets_link = authenticated_browser.find_element_by_link_text("My baskets")
        baskets_link.click()
        create_basket_link = authenticated_browser.find_element_by_link_text(
            "Create basket"
        )
        create_basket_link.click()
        basket_data = dict(name="some-basket", label="Some basket")
        input_basket_name = authenticated_browser.find_element_by_id("id_name")
        input_basket_label = authenticated_browser.find_element_by_id("id_label")
        input_basket_name.send_keys(basket_data["name"])
        input_basket_label.send_keys(basket_data["label"])
        select_study = Select(authenticated_browser.find_element_by_id("id_study"))
        select_study.select_by_visible_text(str(study))
        create_basket_button = authenticated_browser.find_element_by_xpath(
            '//input[@value="Create basket"]'
        )
        create_basket_button.click()

        basket_list = authenticated_browser.find_element_by_css_selector(
            "div.list-group-item"
        )
        assert basket_data["name"] in basket_list.text

        # TODO : assert Basket successfully created. message

    def test_perform_basket(
        self, authenticated_browser, live_server, study, known_user, basket
    ):
        basket.user = known_user
        basket.save()
        authenticated_browser.get(live_server.url + "/workspace/baskets/")
        delete_url = "/workspace/baskets/" + str(basket.pk) + "/delete"
        authenticated_browser.find_element_by_xpath(
            "//a[@href='" + delete_url + "']"
        ).click()
        alert = authenticated_browser.switch_to.alert
        assert alert.text == "Are you sure you want to delete basket " + basket.name + "?"
        alert.accept()


# @pytest.mark.skip(reason="no way of currently testing this")
class TestSearchPage:
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_search_with_known_item(self, selenium, live_server):
        selenium.get(live_server.url + "/search/")
        search_form = selenium.find_element_by_xpath("//input[@placeholder='Search ...']")
        search_form.send_keys("test")
        search_form.send_keys(Keys.ENTER)
        assert "results" in selenium.page_source
        assert "Keep my filters" in selenium.page_source
        assert "Type" in selenium.page_source
        assert "Study" in selenium.page_source
        assert "Analysis unit" in selenium.page_source
        assert "Period" in selenium.page_source

        with pytest.raises(NoSuchElementException):
            selenium.find_element_by_xpath('//button[contains(text(), "Previous")]')
        next_button = selenium.find_element_by_xpath('//button[contains(text(), "Next")]')
        next_button.click()
        previous_button = selenium.find_element_by_xpath(
            '//button[contains(text(), "Previous")]'
        )
        assert previous_button

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_search_with_unknown_item(self, selenium, live_server, settings):
        selenium.get(live_server.url + "/search/")
        search_form = selenium.find_element_by_xpath("//input[@placeholder='Search ...']")
        search_form.send_keys("11111111111111111111111111")
        search_form.send_keys(Keys.ENTER)
        print(settings.INDEX_NAME)
        # assert "No results. Try to change query or filter options." in selenium.page_source

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_search_with_es(self, selenium, live_server, settings, study):
        r = study.set_elastic(
            dict(name=study.name, label=study.label, description=study.description)
        )
        selenium.get(live_server.url + "/search/")
        search_form = selenium.find_element_by_xpath("//input[@placeholder='Search ...']")
        search_form.send_keys("some-study")
        search_form.send_keys(Keys.ENTER)
        print(settings.INDEX_NAME)
        time.sleep(5)


class TestStudySearch:
    pass
