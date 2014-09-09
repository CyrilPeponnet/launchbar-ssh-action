launchbar-ssh-action
====================

Action to establish a new ssh connection based on host history.

Host history is built using the following sources of hosts:

    * '~/.ssh/config'
    * '~/.ssh/known_hosts'
    * '/etc/hosts'
    * '_ssh._tcp' host discovery using bonjour protocol (you need to install pybonjour)

By default ssh:// url handler is Terminal.app, if you want to use iTerm2 instead you have to set a proper URL schemes in iTerm2 pref pane.

![alt tag](http://cl.ly/BEOf/Bildschirmfoto_2011-10-23_um_21.01.41.png)

This actions is inspired from alfred2 ssh workflow by isometry.