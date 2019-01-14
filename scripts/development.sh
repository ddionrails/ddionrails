#!/bin/sh

##
# Activate virtualenv.
#
source ~/.envs/ddionrails2/bin/activate

##
# Initiate tmus session if not existing.
#
tmux has-session -t dor
if [ $? != 0 ]
then
  tmux new-session -s dor -n edit -d
  tmux split-window -h -t dor
  
  tmux new-window -t dor -n work
  tmux split-window -h -t dor:1
  tmux split-window -v -t dor:1.0
  tmux split-window -v -t dor:1.0
  tmux split-window -v -t dor:1.2
  tmux send-keys -t dor:1.0 "paver server" C-m
  tmux send-keys -t dor:1.1 "paver elastic" C-m
  tmux send-keys -t dor:1.2 "paver rqworker" C-m
  tmux send-keys -t dor:1.3 "paver webpack_watch" C-m
  
#  tmux new-window -t dor -n docs
#  tmux split-window -h -t dor:2
#  tmux send-keys -t dor:2.0 "cd ../docs; clear" C-m
#  tmux send-keys -t dor:2.1 "cd ../docs; clear" C-m
#  
#  tmux new-window -t dor -n know
#  tmux split-window -h -t dor:3
#  tmux send-keys -t dor:3.0 "cd ../../knowledge; clear" C-m
#  tmux send-keys -t dor:3.1 "cd ../../knowledge; clear" C-m
fi

##
# Attach tmux session.
#
tmux select-window -t dor:0
tmux select-pane -t dor:0.0
tmux attach -t dor
