#!/bin/sh

# see: https://github.com/mhebing/ddionrails2/issues/365
# man ps: ps -A : Select all processes.  Identical to -e.

ps -A | grep java
ps -A | grep python
