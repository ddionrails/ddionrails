# -*- coding: utf-8 -*-
""" Test cases for ddionrails.api app """

class TestObjectRedirectView:
    def test_variable_redirect(self, client, variable):
        url = f"/api/test/redirect/variable/{variable.id}"
        response = client.get(url)
        assert 302 == response.status_code

    def test_publication_redirect(self, client, publication):
        url = f"/api/test/redirect/publication/{publication.id}"
        response = client.get(url)
        assert 302 == response.status_code

    def test_question_redirect(self, client, question):
        url = f"/api/test/redirect/question/{question.id}"
        response = client.get(url)
        assert 302 == response.status_code

    def test_concept_redirect(self, client, concept):
        url = f"/api/test/redirect/concept/{concept.id}"
        response = client.get(url, follow=True)
        assert 200 == response.status_code
        assert response.redirect_chain[-1][0] == concept.get_absolute_url()
