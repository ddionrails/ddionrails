from click.exceptions import Abort
from django.core.exceptions import ObjectDoesNotExist

import djclick as click
from studies.models import Study
from data.models import Variable

def summary(study):
    num_datasets = study.datasets.count()
    num_instruments = study.instruments.count()
    num_periods = study.periods.count()
    num_baskets = study.baskets.count()
    num_variables = Variable.objects.filter(dataset__study=study).count()
    num_publications = study.publications.count()

    print(f'{num_datasets} related datasets will be deleted')
    print(f'{num_variables} related variables will be deleted')
    print(f'{num_instruments} related instruments will be deleted')
    print(f'{num_periods} related periods will be deleted')
    print(f'{num_baskets} related baskets will be deleted')
    print(f'{num_publications} related publications will be deleted')

    # data.Transformation': 50839,
    # workspace.BasketVariable': 0,
    # instruments.QuestionVariable': 0,
    # publications.Attachment': 0,
    # workspace.Script': 0,


def delete(study):
    print("DELETE", study)
    # result = study.delete()
    # print(result)


@click.command()
@click.argument("study_name")
@click.option("-f", "--force", default=False, is_flag=True)
def command(study_name: str, force: bool) -> None:
    try:
        study = Study.objects.get(name=study_name)
    except ObjectDoesNotExist as exception:
        study = None
        print(exception)
        exit(1)

    if force is True:
        delete(study)
    else:
        try:
            summary(study)
            click.confirm("Do you want to continue?", abort=True)
            delete(study)
        except Abort:
            print("DO NOT DELETE", study)
