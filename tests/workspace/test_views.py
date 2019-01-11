from workspace.views import script_detail


class TestScriptDetailView:
    def test_script_detail_view_with_script_created_before_update(self, rf, basket, script):
        """ This tests a regression that was introduced after updating the settings for scripts
            with a 'gender' option
        """
        script.basket = basket
        # Set the settings to the default values from before the update
        script.settings = (
            '{"path_in": "data/", "path_out": "out/", '
            '"analysis_unit": "p", "private": "t", '
            '"balanced": "t", "age_group": "adult"}'
        )
        script.save()

        request = rf.get("script_detail", basket_id=basket.id, script_id=script.id)
        response = script_detail(request, basket.id, script.id)
        assert response.status_code == 200
