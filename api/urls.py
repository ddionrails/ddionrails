from django.conf.urls import url
from django.urls import path

from data.views import variable_preview_id
from instruments.views import question_comparison_partial

from .views import (
    add_variable_by_id,
    add_variables_by_concept,
    add_variables_by_topic,
    baskets_by_study_and_user,
    concept_by_study,
    object_redirect,
    test_preview,
    # test_redirect,
    test_rq,
    topic_by_study,
    topic_list,
)

app_name = "api"

urlpatterns = [
    path("test/rq", test_rq, name="test_rq"),
    path(
        "test/preview/variable/<int:variable_id>",
        variable_preview_id,
        name="variable_preview",
    ),
    path(
        "test/preview/<str:object_type>/<int:object_id>",
        test_preview,
        name="test_preview",
    ),
    # path(
    #     "test/redirect/<str:object_type>/<int:object_id>",
    #     test_redirect,
    #     name="test_redirect",
    # ),
    #######
    url(
        r"^questions/compare/(?P<from_id>[0-9]+)/(?P<to_id>[0-9]+)$",
        question_comparison_partial,
    ),
    url(
        r"^test/redirect/(?P<object_type>[A-Za-z]+)/(?P<object_id>[a-z0-9_\-]+)$",
        object_redirect,
        name="object_redirect",
    ),
    url(
        r"^topics/redirect/(?P<object_type>[A-Za-z]+)_(?P<object_id>[a-z0-9_\-]+)$",
        object_redirect,
        name="object_redirect",
    ),
    url(r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)$", topic_list),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/concept_(?P<concept_name>[a-z0-9\-_]+)$",
        concept_by_study,
    ),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/topic_(?P<topic_name>[a-z0-9\-_]+)$",
        topic_by_study,
    ),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/baskets$",
        baskets_by_study_and_user,
    ),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/concept_(?P<concept_name>[a-z0-9\-_]+)/add_to_basket/(?P<basket_id>[a-z0-9\-_]+)$",
        add_variables_by_concept,
    ),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/topic_(?P<topic_name>[a-z0-9\-_]+)/add_to_basket/(?P<basket_id>[a-z0-9\-_]+)$",
        add_variables_by_topic,
    ),
    url(
        r"^topics/(?P<study_name>[a-z0-9\-_]+)/(?P<language>[a-z0-9\-_]+)/variable_(?P<variable_id>[a-z0-9\-_]+)/add_to_basket/(?P<basket_id>[a-z0-9\-_]+)$",
        add_variable_by_id,
    ),
]
