from cryptography.fernet import Fernet
from enum import Enum

class Operation(Enum):
    ENCRYPT = 0
    DECRYPT = 1
    FILE_SELECT = 2
    FOLDER_SELECT = 3

class FileInterface(object):
    @classmethod
    def save(cls, full_name, type, content, cast=None):
        try:
            with open(full_name, type) as file:
                if cast:
                    content = cast(content)
                file.write(content)
        except IOError as err:
            print str(err)

    @classmethod
    def load(cls, full_name, type, cast=None):
        try:
            with open(full_name, type) as file:
                content = file.read()
                return cast(content) if cast else content
        except IOError as err:
            print str(err)
            return None

class EncEngine(object):
    key = None
    kernel = None
    target = []

    def __init__(self):
        pass

    def save_key_as(self, path):
        # save key to specified file
        FileInterface.save(path, 'w', self.key)

    def load_key(self, path):
        # get key from file
        self.key = bytes(FileInterface.load(path, 'r'))
        
        # re instantiate kernel
        self.kernel = Fernet(self.key)
        pass

    def gen_key(self):
        self.key = Fernet.generate_key()
        # re instantiate kernel
        self.kernel = Fernet(self.key)

    def get_key(self):
        return self.key

    @property
    def target_(self):
        return self.target

    @target_.setter
    def target_(self, path):
        self.target = path

    def run(self,
            optype=Operation.ENCRYPT,
            ftype=Operation.FILE_SELECT):
        #
        # f_list = []
        #
        # if ftype == Operation.FOLDER_SELECT:
        # # Extract files from folder path
        #     pass
        # elif ftype == Operation.FILE_SELECT:
        # # work on file path
        #     f_list = [f]

        for file in self.target:
            self._encrpt(file, optype)

    def _encrpt(self, f, optype):
        token = None

        content = bytes(FileInterface.load(f,
                                           'rb'))
        print type(content)
        if content:
            if optype == Operation.ENCRYPT:
                token = self.kernel.encrypt(content)
            elif optype == Operation.DECRYPT:
                token = self.kernel.decrypt(content)
            FileInterface.save(f, 'wb', token)
