# pylint: disable=R0902
from dataclasses import dataclass


@dataclass
class TopicData: ...


@dataclass
class ConceptData: ...


@dataclass
class PeriodData: ...


@dataclass
class AnalysisUnitData: ...


@dataclass
class ConceptualDatasetData: ...


@dataclass
class StudyData:
    name: str = "test_study"
    label: str = "study_label"
    label_de: str = "study_label_de"
    description: str = ""
    description_de: str = ""
    doi: str = ""
    vesion: str = ""
    pin_reference: str = ""
    repo: str = ""
    webhook_secret: str = ""
    current_commit: str = ""
    config: dict = {}
    topic_languages: list = []
    menu_order: int = 1
    topiclist: list[TopicData] = []


@dataclass
class DatasetData:
    name: str = "test_dataset"
    label: str = "dataset_label"
    label_de: str = "dataset_label"
    description: str = ""
    description_de: str = ""
    folder: str = ""
    primary_key: list[str] = ["pid"]
    study: StudyData = StudyData()
    conceptual_dataset: ConceptualDatasetData = ConceptualDatasetData()
    period: PeriodData = PeriodData()
    analysis_unit: AnalysisUnitData = AnalysisUnitData()


@dataclass
class VariableData:
    name: str = "test_variable"
    label: str = "variable_label"
    label_de: str = "variable_label"
    description: str = ""
    description_de: str = ""
    description_long: str = ""
    sort_id: int = 0
    image_url: str = ""
    pid: str = ""
    statistics: dict = {}
    scale: str = ""
    statistics_flag: bool = False
    categories: dict = {}
    concept: ConceptData = ConceptData()
    dataset: DatasetData = DatasetData()
    images: dict = {}
    period: PeriodData = PeriodData()


@dataclass
class InstrumentData:
    name: str = "test_variable"
    label: str = "variable_label"
    label_de: str = "variable_label"
    description: str = ""
    description_de: str = ""
    mode: str = ""
    type: dict = {}
    has_questions: bool = False
    study: StudyData = StudyData()
    datasets: list[DatasetData] = []
    period: PeriodData = PeriodData()
    analysis_unit: AnalysisUnitData = AnalysisUnitData()


@dataclass
class QuestionItemData: ...


@dataclass
class QuestionData:
    name: str = "test_variable"
    label: str = "variable_label"
    label_de: str = "variable_label"
    description: str = ""
    description_de: str = ""
    instruction: str = ""
    instruction_de: str = ""
    sort_id: int = 0
    items: dict = {}  # TODO: What is this in relation to question_items?
    question_items: list[QuestionItemData] = []
    images: dict = {}
    instrument: InstrumentData = InstrumentData()
    period: PeriodData = PeriodData()
    # TODO: How are the relations between question and variables called?
