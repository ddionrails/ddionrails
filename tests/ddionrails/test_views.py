import pytest
from django.urls import reverse

from ddionrails.views import (
    HomePageView,
    bad_request,
    contact_page,
    elastic_proxy,
    elastic_test,
    imprint_page,
    page_not_found,
    permission_denied,
    quick_page,
    server_error,
)


class TestPageViews:
    def test_contact_page(self, rf, db):
        url = reverse("contact")
        request = rf.get(url)
        response = contact_page(request)
        assert response.status_code == 200
        content = str(response.content)
        assert "Contact / feedback" in content
        assert "SOEP Hotline" in content
        assert "Github" in content

    def test_home_page(self, rf, db):
        url = reverse("homepage")
        request = rf.get(url)
        response = HomePageView.as_view()(request)
        assert response.status_code == 200

    def test_imprint_page(self, rf, db):
        url = reverse("imprint")
        request = rf.get(url)
        response = imprint_page(request)
        assert response.status_code == 200
        content = str(response.content)
        assert "Imprint" in content
        assert "Privacy policy at DIW Berlin" in content

    def test_quick_page(self, rf, db):
        url = reverse("quickpage")
        request = rf.get(url)
        response = quick_page(request)
        assert response.status_code == 200
        content = str(response.content)
        assert "Quick links" in content


class TestElasticViews:
    def test_elastic_test(self, rf, db):
        url = reverse("elastic_test")
        request = rf.get(url)
        response = elastic_test(request)
        assert response.status_code == 200
        content = str(response.content)
        assert "Imprint" in content
        assert "Loading" in content
        assert "javascript" in content

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_elastic_proxy(self):
        pytest.fail("Test not implemented yet")


class TestErrorTemplates:
    def test_400_template(self, rf, db):
        url = reverse("homepage")
        request = rf.get(url)
        response = bad_request(request, exception="")
        assert response.status_code == 400
        assert "Bad Request (400)" in str(response.content)

    def test_403_template(self, rf, db):
        url = reverse("homepage")
        request = rf.get(url)
        response = permission_denied(request, exception="")
        assert response.status_code == 403
        assert "Forbidden (403)" in str(response.content)

    def test_404_template(self, rf, db):
        url = reverse("homepage")
        request = rf.get(url)
        response = page_not_found(request, exception="")
        assert response.status_code == 404
        assert "Page not found (404)" in str(response.content)

    def test_500_template(self, rf, db):
        url = reverse("homepage")
        request = rf.get(url)
        response = server_error(request, exception="")
        assert response.status_code == 500
        assert "Internal Server Error (500)" in str(response.content)
