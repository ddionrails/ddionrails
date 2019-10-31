# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Vi like movement in interactive bash shell
set -o vi

export LS_OPTIONS='--color=auto'
eval "`dircolors`"
alias ls='ls $LS_OPTIONS'
export force_color_prompt=yes
export TERM=xterm-256color
color_prompt=yes
PS1='${debian_chroot:+($debian_chroot)}\[\033[01;31m\]\u\[\033[01;30m\]@\[\033[01;30m\]\h\[\033[00m\]:\[\033[001;34m\]\w\[\033[00m\]\$ '

bind -m vi-insert "\C-l":clear-screen
bind -m vi-command "\C-l":clear-screen

if [ -d "${HOME}/.gnupg" ]; then
  git config --global user.signingkey $(gpg --list-secret-keys --keyid-format LONG | sed -En "s/^sec.*\/([A-Z0-9]*)\s.*$/\1/p")
  export GPG_TTY=$(tty)
fi
