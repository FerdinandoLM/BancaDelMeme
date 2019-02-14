#!/bin/bash
tmux kill-session -t mememain
tmux kill-session -t memesub
tmux kill-session -t memecalc
#tmux kill-session -t memepayroll

/bin/sleep 1
source /home/ribre/.bashrc
/usr/bin/tmux new-session -d -s mememain
/usr/bin/tmux send-keys -t mememain "source /home/ribre/.bashrc" C-m
/usr/bin/tmux send-keys -t mememain "cd BancaDelMeme" C-m
/usr/bin/tmux send-keys -t mememain "cd src" C-m
/usr/bin/tmux send-keys -t mememain "python3 main.py" C-m

/bin/sleep 1
source /home/ribre/.bashrc
/usr/bin/tmux new-session -d -s memesub
/usr/bin/tmux send-keys -t memesub "source /home/ribre/.bashrc" C-m
/usr/bin/tmux send-keys -t memesub "cd BancaDelMeme" C-m
/usr/bin/tmux send-keys -t memesub "cd src" C-m
/usr/bin/tmux send-keys -t memesub "python3 submitter.py" C-m

/bin/sleep 1
source /home/ribre/.bashrc
/usr/bin/tmux new-session -d -s memecalc
/usr/bin/tmux send-keys -t memecalc "source /home/ribre/.bashrc" C-m
/usr/bin/tmux send-keys -t memecalc "cd BancaDelMeme" C-m
/usr/bin/tmux send-keys -t memecalc "cd src" C-m
/usr/bin/tmux send-keys -t memecalc "python3 calculator.py" C-m

#/bin/sleep 1
#source /home/ribre/.bashrc
#/usr/bin/tmux new-session -d -s memepayroll
#/usr/bin/tmux send-keys -t memepayroll "source /home/ribre/.bashrc" C-m
#/usr/bin/tmux send-keys -t memepayroll "cd BancaDelMeme" C-m
#/usr/bin/tmux send-keys -t memepayroll "cd src" C-m
#/usr/bin/tmux send-keys -t memepayroll "python3 payroll.py" C-m

