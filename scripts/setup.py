import sys
sys.path.append(".")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")
import django
 
def setup():
    django.setup()
