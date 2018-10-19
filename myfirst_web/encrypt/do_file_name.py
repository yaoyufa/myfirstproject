import uuid
import os
def do_file_name(value):
    return str(uuid.uuid1())+os.path.splitext(value)[1]