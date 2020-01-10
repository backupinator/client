'''Client class.'''

class Client:
    '''Implements client API.'''

    def __init__(self):
        # Every client needs a unique name
        self.client_name = 'temp_name'

    def add_file(self, filename):
        '''Add file for backup.'''

        with open(filename, 'rb') as _f:
            pass

    def send_backup(self, filename, target_name):
        '''Send a file to a list of targets.'''

        with open(filename, 'rb') as _f:
            print(target_name)

    def get_manifest(self, target_name):
        '''Get the list of client files present on a target.'''
        print(target_name)

if __name__ == '__main__':

    client = Client()
