import hashlib
def my_md5(value):
    m=hashlib.md5()
    m.update(value.encode("utf-8"))
    return m.hexdigest()