# from itsdangerous import TimedJSONWebSignatureSerializer as TJSSerializer
from itsdangerous import TimedJSONWebSignatureSerializer as TJSSerializer
from django.conf import settings
from itsdangerous import BadData


def generate_save_user_token(openid):
    serirlizer = TJSSerializer(settings.SECRET_KEY, 600)
    data = {'openid': openid}
    token = serirlizer.dumps(data)
    return token.decode()



def check_save_user_token(access_token):
    serializer = TJSSerializer(settings.SECRET_KEY, 600)
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        openid = data.get('openid')
        return openid
