class TestObjectRedirectView:
    def test_variable_redirect(self, client, variable):
        url = "/api/test/redirect/variable/1"
        response = client.get(url)
        assert 302 == response.status_code

    def test_publication_redirect(self, client, publication):
        url = "/api/test/redirect/publication/1"
        response = client.get(url)
        assert 302 == response.status_code

    def test_question_redirect(self, client, question):
        url = "/api/test/redirect/question/1"
        response = client.get(url)
        assert 302 == response.status_code

    def test_concept_redirect(self, client, concept):
        url = "/api/test/redirect/concept/1"
        response = client.get(url, follow=True)
        assert 200 == response.status_code
        assert response.redirect_chain[-1][0] == concept.get_absolute_url()
