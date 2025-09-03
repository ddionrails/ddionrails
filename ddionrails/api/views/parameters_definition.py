"""Definition of query parameters for API endpoints."""

from drf_spectacular.utils import OpenApiParameter

STUDY_PARAMETER = OpenApiParameter(
    "study", description="The name of a study to filter elements to."
)
PAGINATE_PARAMETER = OpenApiParameter("paginate", default="True")
DATASET_PARAMETER = OpenApiParameter(
    "dataset",
    description=(
        "Name of a dataset to filter variables by. "
        "If this is not given, topic or concept needs to be given. "
        "If it is set, study needs to be given as well."
    ),
)
INSTRUMENT_PARAMETER = OpenApiParameter(
    "instrument",
    description=(
        "Name of an instrumen to filter questions by. "
        "If this is not given, topic or concept needs to be given. "
        "If it is set, study needs to be given as well."
    ),
)
TOPIC_PARAMETER = OpenApiParameter(
    "topic",
    description=(
        "Name of a topic to filter questions or variables by. "
        "If topic is not given an instrument for questions, "
        "dataset for variables or concept needs to be given. "
        "If topic is set concept cannot be set."
    ),
)

CONCEPT_PARAMETER = OpenApiParameter(
    "concept",
    description=(
        "Name of a concept to filter questions or variables by. "
        "If concept is not given an instrument for questions, "
        "dataset for variables or topic needs to be given. "
        "If concept is set topic cannot be set."
    ),
)
VARIABLES_PARAMETER = OpenApiParameter(
    "variables[]",
    description=("List of variables to get questions related to these variables."),
)
