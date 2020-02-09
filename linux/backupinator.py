'''Another go at backupinator.

Notes
-----
In this version, we always have a local backup as well as a
repository of patches.  The repository of patches is replicated on
the remotes.

A backup is made up of a set of patches.  When all patches have been
applied, the current version should result.  Any version is also
recoverable.

Problems so far:
    - Uses Linux specific commands (diff and patch)
        - Might be able to use git diff/apply
        - Only need diff for Windows client, patch can be done on
          Linux when needed
        - Could use winmerge
        - Does built-in Windows FC command do the right thing?
    - Seems like sometimes watchdog doesn't catch some events
        - Will need to validate periodically
    - Also need to test more watchdog events
    - We're having to make sure each file exists before doing diff
        - Means we are looping through directories recursively
        - Could be very expensive, need to do better book-keeping so
          we don't have to do this
    - diff and patch might not work so well for large files, need a
      better strategy for that
        - Might be able to assume that large files do not change
          often, so might be a non-issue
        - or just set a threshold size: if above, send patch to
          delete file then patch to create the new one
'''

import pathlib
import logging
from time import time
import subprocess

from watchdog.events import ( # pylint: disable=E0401
    FileSystemEventHandler)

def send_patch(_patch, _remote):
    '''Send the patch to remote backup location.'''

def make_patch(dirpath):
    '''Make a patch for an entire directory.'''

    backup = pathlib.Path('backup/files')
    backup.mkdir(exist_ok=True, parents=True)
    patches = pathlib.Path('backup/patches')
    patches.mkdir(exist_ok=True, parents=True)

    # Make sure all files exist in backup directory
    for p in dirpath.glob('**/*'):
        target = backup / p
        if not target.exists():
            if p.is_dir():
                target.mkdir(parents=True)
            else:
                target.parent.mkdir(exist_ok=True, parents=True)
                target.touch()

    # Make and apply the patch
    patchfile = (patches / str(time())).with_suffix('.patch')
    with open(patchfile, 'w') as pf:
        res = subprocess.Popen(
            ['diff', '-ruN', str(backup / dirpath), str(dirpath)],
            stdout=pf)
    print(res)

    with open(patchfile, 'r') as pf:
        res = subprocess.Popen(
            ['patch', '-s', '-p0', '-d' + str(backup.absolute())],
            stdin=pf)
    print(res)

class EventHandler(FileSystemEventHandler):
    '''Handle watchdog events.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_time = time()

    def on_modified(self, ev):
        '''Send a patch to all backups.'''

        # Sometimes events come in clusters (e.g. flush and close),
        # so make sure we filter these out
        if time() - self.last_time < 1:
            logging.info('DEBOUNCED')
            return
        self.last_time = time()

        logging.info('DIRECTORY MODIFICATION')
        filename = pathlib.Path(ev.src_path)
        if not filename.is_dir():
            make_patch(filename.parent)
        else:
            make_patch(filename)

if __name__ == '__main__':

    from time import sleep
    from watchdog.observers import Observer # pylint: disable=E0401

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Make a directory to try it out in
    test = pathlib.Path('./test/')
    test.mkdir(exist_ok=True)
    print(str(test))

    # Start the watchdog
    observer = Observer()
    event_handler = EventHandler()
    observer.schedule(event_handler, str(test), recursive=True)
    observer.start()

    # Create a file
    testfile = test / 'testfile.txt'
    if testfile.exists():
        testfile.unlink()
    testfile.touch()

    # Give it some time find it
    sleep(1)

    # Modify the file
    with open(testfile, 'a') as f:
        f.write('Hello, world!\n')
    # input()

    # Give it some time to find it
    sleep(1)

    # Modify again
    with open(testfile, 'a') as f:
        f.write('Here is another thing.\n')
    # input()

    sleep(1)

    # Create a another file
    testfile2 = test / 'testfile2.txt'
    with open(testfile2, 'w') as f, open(testfile, 'a') as g:
        f.write('Howdy, I am number 1.\n')
        g.write('I happen to be number 2 this time.\n')

    sleep(1)
    # input()

    # Remove file
    testfile.unlink()
    testfile2.unlink()

    # Give it some time find it
    sleep(2)

    # Stop the watchdog
    observer.stop()
    observer.join()
