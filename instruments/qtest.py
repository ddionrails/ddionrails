from instruments.models import Question
import difflib

def run():
    q = Question.objects.get(pk=38)
    print(q.get_source())
    print("--------------------------------------------------")
    print(q.comparison_string(to_string=True))
    with open("local/qtest.html", "w+") as f:
        f.write(difflib.HtmlDiff().make_file(
            ["Was", "für", "ein", "Tag"],
            ["Was", "fuer", "ein", "Tag"],
            fromdesc="alt",
            todesc="neu",
        ))
    print("--------------------------------------------------")
    q3 = Question.objects.get(pk=3)
    print("Test for question 3: %s" % q3)
    print("Concepts: %s" % q3.get_concepts())
    print("Related questions: %s" % q3.get_related_question_set())
    print("Related questions: %s" % q3.get_related_question_set(all_studies=True))
    print("Related questions: %s" % q3.get_related_question_set(all_studies=True, by_study_and_period=True))
