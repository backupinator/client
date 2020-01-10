Client
======

Application running in background on client machine.

API
===

add_file(filename)
  Add file for backup.

send_backup(filename, target_names)
  Send a file to a list of targets.

get_manifest(target_name):
  Get the list of client files present on a target.
