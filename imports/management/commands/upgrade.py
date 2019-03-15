import djclick as click

from studies.models import Study

from imports.manager import StudyImportManager

from .update import update_study


@click.command()
@click.option("-s", "--study", "study_name", default=False)
@click.option("--all", "_all", default=False, is_flag=True)
@click.option("-a", "--analysis_units", default=False, is_flag=True)
@click.option("-p", "--periods", default=False, is_flag=True)
@click.option("-v", "--variables", default=False, is_flag=True)
@click.option("-d", "--datasets", default=False, is_flag=True)
@click.option("-i", "--instruments", default=False, is_flag=True)
@click.option("-t", "--transformations", default=False, is_flag=True)
@click.option("-qv", "--questions_variables", default=False, is_flag=True)
@click.option("-cq", "--concepts_questions", default=False, is_flag=True)
@click.option("-u", "--update", default=False)
@click.option("--filename")
def command(
    study_name,
    variables,
    analysis_units,
    filename,
    periods,
    update,
    datasets,
    instruments,
    questions_variables,
    concepts_questions,
    transformations,
    _all
):
    if _all is True:
        print("upgrade all studies")
        for study in Study.objects.all():
            print("upgrade study", study)
            update_study(study)
            manager = StudyImportManager(study)
            manager.import_all_entities()
        exit(0)

    else:
        try:
            study = Study.objects.get(name=study_name)
        except Exception as e:
            print(e)
            exit(1)
        if update:
            update_study(study)

        manager = StudyImportManager(study)
        if (
            any(
                (
                    analysis_units,
                    periods,
                    variables,
                    datasets,
                    instruments,
                    questions_variables,
                    concepts_questions,
                    transformations,
                )
            )
            is False
        ):
            print("upgrade all entities")
            manager.import_all_entities()
        else:
            if variables:
                manager.import_single_entity("variables")
            if periods:
                manager.import_single_entity("periods")
            if datasets:
                if filename:
                    manager.import_single_entity("datasets.json", filename)
                else:
                    manager.import_single_entity("datasets.json")
                    manager.import_single_entity("datasets.csv")
            if instruments:
                if filename:
                    manager.import_single_entity("instruments", filename)
                else:
                    manager.import_single_entity("instruments")
            if questions_variables:
                print("questions_variables")
                manager.import_single_entity("questions_variables")

            if concepts_questions:
                print("concepts_questions")
                manager.import_single_entity("concepts_questions")
            if transformations:
                print("transformations")
                manager.import_single_entity("transformations")
