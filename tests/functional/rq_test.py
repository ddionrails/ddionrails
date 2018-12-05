#!/usr/bin/env python

import time
from data.models import Variable
import django_rq

def vc():
    x = Variable.objects.count()
    print("NUMBER OF VARIABLES:", x)
    return x

def run():
    django_rq.enqueue(print, "hi")
    django_rq.enqueue(vc)
    django_rq.enqueue(time.sleep, 1)

if __name__ == "__main__":
    run()
