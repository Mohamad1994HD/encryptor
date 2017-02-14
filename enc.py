import cryptography
from cryptography.fernet import Fernet
from enum import Enum
import os

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

class InvalidOperationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

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
        self.target = []
        if os.path.isdir(path):
            for p_, subdirs, files in os.walk(path):
                for name in files:
                    self.target.append(os.path.join(path, name))
        else:
            self.target = [path]


    def run(self,
            optype=Operation.ENCRYPT):
        if not self.kernel:
            raise InvalidOperationError("""No Key was used, either generate a new key
                                           \ror select existing key on your device""")
        try:
            for file in self.target:
                self._encrpt(file, optype)
        except cryptography.fernet.InvalidToken as err:
            msg = """Error Invalid operation Maybe you are decrypting
                     \runencrypted file or you are using invalid key"""

            raise InvalidOperationError(msg)

    def _encrpt(self, f, optype):
        token = None

        content = bytes(FileInterface.load(f,
                                           'rb'))
        if content:
            if optype == Operation.ENCRYPT:
                token = self.kernel.encrypt(content)
            elif optype == Operation.DECRYPT:
                token = self.kernel.decrypt(content)
            FileInterface.save(f, 'wb', token)
