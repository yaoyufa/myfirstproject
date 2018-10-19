from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client

class FDFSStorage(Storage):
    def __init__(self):
        self.client_conf=settings.FDFS_CLIENT_CONF
        self.base_url=settings.FDFS_URL
    def _open(self,name,mode='rb'):
        pass
    def _save(self,name,content):
        client = Fdfs_client(self.client_conf)
        res = client.upload_by_buffer(content.read())
        print('res',res)
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FastDFS失败')
        filename = res.get('Remote file_id').decode()
        return  filename
    def exists(self, name):
        return False

    def url(self, name):
        return self.base_url + name