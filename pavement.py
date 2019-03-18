"""
Pavement file
"""
import os
import shutil
import socket
import sys

import django
from django.conf import settings
from django.core import management
from paver.easy import consume_args, needs, task

sys.path.append(".")

hostname = socket.gethostname()

if hostname == "hewing":
    local_settings = "hewing"
elif hostname == "paneldata":
    local_settings = "production"
else:
    local_settings = "development"

print("[INFO] Using %s settings." % local_settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.%s" % local_settings)


# Helper functions


def info(text):
    print("\n[INFO] %s" % text)


def run(script):
    for line in script.strip().split("\n"):
        print("\n[SYSTEM] %s" % line.strip())
    os.system(script)


def init_development_db():
    """Init development database."""
    django.setup()
    run("rm -f db/db.sqlite3")
    management.call_command("migrate")


def elastic_server():
    return "%s:%s/%s" % (settings.INDEX_HOST, settings.INDEX_PORT, settings.INDEX_NAME)


# Tasks


@task
def which_system():
    print("[INFO] System repo:  ", settings.SYSTEM_REPO_URL)
    print("[INFO] Import branch:", settings.IMPORT_BRANCH)


@task
def rqworker():
    """Start Redis worker."""
    django.setup()
    management.call_command("rqworker")


@task
def install_elastic():
    """Install Elasticsearch."""
    run(
        """
        rm -rf db/elasticsearch
        wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.4.2/elasticsearch-2.4.2.tar.gz
        tar xzvf elasticsearch*.tar.gz
        rm elasticsearch*.tar.gz
        mv elasticsearch* db/elasticsearch
    """
    )


@task
def elastic():
    """Start Elasticsearch as a foreground process."""
    run("./db/elasticsearch/bin/elasticsearch")


@task
def delete_index():
    "Delete the index."
    run("curl -XDELETE '%s'" % elastic_server())
    print()


@task
def create_index():
    "Create the index from the elastic/mapping.json file."
    run("curl -s -XPOST '%s' -d@elastic/mapping.json" % elastic_server())
    print()


@task
def reset_index():
    """Delete index, update mapping, create index."""
    delete_index()
    run("yaml2json elastic/mapping.yaml > elastic/mapping.json")
    create_index()


@task
def docu():
    """Run the docu make script (no delete)."""
    run("cd ../docs; make html")


@task
def full_docu():
    """Completely rebuild the docu."""
    run("cd ../docs; rm -r _build; make html")


@task
def fire_docu():
    """Open docu in Firefox."""
    run("firefox ../docs/_build/html/index.html")


@task
def chrome_docu():
    """Open docu in Google Chrome."""
    run("google-chrome ../docs/_build/html/index.html")


@task
def server():
    """Start development server."""
    django.setup()
    management.call_command("runserver_plus")


@task
def setup_virtualenv():
    """Setup virtualenv in: ~/.envs/ddionrails2/"""
    run(
        """
        mkdir -p ~/.envs
        virtualenv -p /usr/bin/python3.4 ~/.envs/ddionrails2
        source ~/.envs/ddionrails2/bin/activate
        pip install -r requirements.txt
    """
    )


@task
def freeze_requirements():
    """Freeze requirements."""
    run("pip freeze > requirements.txt")


@task
def test_env():
    """Rebuild the database and delete all repositories."""
    django.setup()
    run(
        """
        rm db/db.sqlite3
        ./manage.py migrate
        rm -rf static/repositories/*
        touch static/repositories/.gitkeep
        chmod 666 db/db.sqlite3
    """
    )
    delete_index()
    create_index()


@task
def test_su():
    """Create superuser "admin" with password "testtest"."""
    from django.contrib.auth.models import User

    django.setup()
    User.objects.create_superuser("admin", "admin@example.com", "testtest")


@task
def import_system():
    """Run scripts: system."""
    django.setup()
    run("./manage.py runscript scripts.system --settings=settings.%s" % local_settings)


@task
def import_all_studies():
    """Run scripts: import."""
    django.setup()
    management.call_command("update", "--all")
    management.call_command("upgrade", "--all")


@task
def copy_secrets_file():
    """ Copy the secrets.json.example and rename it to secrets.json """
    shutil.copyfile("secrets.json.example", "secrets.json")


@task
def full_test():
    """Rebuild the test environment and import data."""
    copy_secrets_file()
    django.setup()
    test_env()
    if local_settings == "development":
        test_su()
    import_system()
    import_all_studies()


@task
def clean_cache():
    run("py3clean .")


@task
def reset_migrations():
    """Reset all migrations."""
    django.setup()
    clean_cache()
    run(
        """
            rm */migrations/0*
            ./manage.py makemigrations
        """
    )


@task
def full_push():
    """Merge development branch into master and push all branches."""
    run(
        """
            git checkout master
            git merge development
            git checkout development
            git push --all
        """
    )


@task
def erd():
    """Create and open ERD file"""
    django.setup()
    run(
        """
            ./manage.py graph_models -a > local/erd.dot
            cd local
            dot erd.dot -T pdf > erd.pdf
            evince erd.pdf
        """
    )


@task
def shell():
    """Use django-extensions shell_plus."""
    django.setup()
    management.call_command("shell_plus")


@task
def migrate():
    """Make and run migrations."""
    django.setup()
    management.call_command("makemigrations")
    management.call_command("migrate")


@task
def rq_test():
    """Test the RQ worker."""
    django.setup()
    run("""./manage.py runscript scripts.rq_test""")


@task
def zip_elastic():
    """Create a ZIP file of the elastic directory"""
    run(
        """
            cd db
            rm elastic.zip
            zip -r elastic.zip elasticsearch/
        """
    )


@task
def elastic_search_javascript_library():
    """ Build the search library for ddionrails """
    # TODO: This is a workaround. The library should be bundled with webpack directly.
    # see: https://v5.angular.io/guide/webpack
    # see: https://www.twilio.com/blog/2018/03/building-an-app-from-scratch-with-angular-and-webpack.html
    run(
        """
            cd ./node_modules/ddionrails-elasticsearch
            npm install
            ./node_modules/.bin/ng build --prod
        """
    )


@task
def webpack():
    """ Create webpack bundles """
    run("""./node_modules/.bin/webpack --config webpack.config.js""")


@task
def webpack_watch():
    """ Watch webpack bundles (in development) """
    run(
        """./node_modules/.bin/webpack --config webpack.config.js --watch --debug --devtool source-map"""
    )


@task
def setup_frontend():
    """ Setup all frontend dependencies """
    run("""npm install""")
    elastic_search_javascript_library()
    webpack()


@task
def setup_pipenv():
    run("""pipenv install --dev""")


@task
def init():
    setup_pipenv()
    setup_frontend()


@task
def test():
    """ Test the project without selenium tests """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.testing")
    django.setup()
    run("""pytest -v -m "not functional" """)


@task
def system_test():
    """ Test the project with selenium tests """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.testing")
    django.setup()
    run("""pytest -v -m functional """)


@task
@needs("install_elastic", "setup_frontend", "copy_secrets_file", "migrate")
def initial_setup():
    """Run initial commands to setup DDI on Rails after download"""
    pass


@task
@consume_args
def update_study(args):
    """Update repo of a study and import all files, one argument: study-name"""
    django.setup()
    from studies.models import Study
    from imports.manager import StudyImportManager, Repository

    study_name = args[0]
    study = Study.objects.get(name=study_name)
    Repository(study).update_or_clone_repo()
    StudyImportManager(study).import_all_entities()
