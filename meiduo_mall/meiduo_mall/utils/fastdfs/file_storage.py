from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储系统"""
    def __init__(self, client_conf=None, base_url=None):
        """初始化文件存储对象的构造方法"""
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        # 创建对接fdfs客户端对象
        client = Fdfs_client(self.client_conf)

        ret = client.upload_by_buffer(content.read())

        if ret.get('Status') != 'Upload successed.':
            raise Exception('upload file failed')

        file_id = ret.get('Remote file_id')

        return file_id

    def exists(self, name):
        return False

    def url(self, name):

        return self.base_url + name
