import logging
from django.shortcuts import render
#
# import logging
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from QQLoginTool.QQtool import OAuthQQ
# from django.conf import settings
# from .models import OAuthQQUser
# from rest_framework_jwt.views import api_settings
# from .utils import generate_save_user_token
# from .serializers import QQAuthUserSerializer
# from rest_framework.generics import GenericAPIView
#
# # Create your views here.
#
# logger = logging.getLogger('django')
#
#
# class QQAuthUserView(GenericAPIView):
#     """处理qq扫码回调: 完成oauth2.0认证过程"""
#
#     serializer_class = QQAuthUserSerializer
#
#     def get(self, request):
#         # 提取code请求参数
#         code = request.query_params.get('code')
#         if not code:
#             return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
#         # 创建oauth对象
#         oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
#
#         try:
#             # 使⽤code向QQ服务器请求access_token
#             access_token = oauth.get_access_token(code)
#             # 使⽤access_token向QQ服务器请求openid
#             openid = oauth.get_open_id(access_token)
#         except Exception as e:
#             logger.info(e)
#             return Response({'message': 'QQ服务器内部错误'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
#         # 使⽤openid查询该QQ⽤户是否在美多商城中绑定过⽤户
#         try:
#             oauthqquser_model = OAuthQQUser.objects.get(openid=openid)
#         except OAuthQQUser.DoesNotExist:
#             # 如果openid没绑定美多商城⽤户，创建⽤户并绑定到openid
#             # 将openid响应给浏览器,方便后面绑定user(加个密)
#             openid_access_token = generate_save_user_token(openid)
#             return Response({'access_token': openid_access_token})
#         else:
#             # 如果openid已绑定美多商城⽤户，直接⽣成JWT token，并返回
#             jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#             jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#             user = oauthqquser_model.user
#             payload = jwt_payload_handler(user)
#             token = jwt_encode_handler(payload)
#
#             return Response({
#                 'username': user.username,
#                 'user_id': user.id,
#                 'token': token
#             })
#
#     def post(self, request):
#         """
#         绑定openid到美多账户
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#
#         return Response({
#             'token': token,
#             'user_id': user.id,
#             'username': user.username
#         })
#
#
# class QQAuthURLView(APIView):
#     """返回qq扫码登录链接"""
#
#     def get(self, request):
#         next = request.query_params.get('next')
#         if not next:
#             next = '/'
#         oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
#         login_url = oauth.get_qq_url()
#         return Response({'login_url': login_url})






from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import OAuthQQUser
from rest_framework_jwt.views import api_settings
from .utils import generate_save_user_token
from rest_framework.generics import GenericAPIView
from .serializers import QQAuthUserSerializer
from carts.utils import merge_cart_cookie_to_redis

logger = logging.getLogger('django')


class QQAuthUserView(GenericAPIView):
    """处理扫码之后的回调, 完成oauth2.0认证"""

    serializer_class = QQAuthUserSerializer

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response({'message': 'QQ服务器内部错误'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            oauthuser_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            openid_access_token = generate_save_user_token(openid)
            return Response({'access_token': openid_access_token})
        else:
            # 必须在注册或者登录之后，响应注册或者登录结果之前，生成jwt_token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            user = oauthuser_model.user
            # 生成载荷：包含了user_id,username,email
            payload = jwt_payload_handler(user)
            # jwt_token
            token = jwt_encode_handler(payload)
            # 将token添加到user : python是面向对象的高级动态编程语言
            # 合并购物车
            response = Response({
                'user_id': user.id,
                'username': user.username,
                'token': token
            })
            response = merge_cart_cookie_to_redis(request, response, user)
            return response

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷：包含了user_id,username,email
        payload = jwt_payload_handler(user)
        # jwt_token
        token = jwt_encode_handler(payload)
        # 将token添加到user : python是面向对象的高级动态编程语言
        # 合并购物车
        response = Response({
            'user_id': user.id,
            'username': user.username,
            'token': token
        })
        response = merge_cart_cookie_to_redis(request, response, user)
        return response


class QQAuthURLView(APIView):
    """返回QQ登录url"""
    def get(self, request):
        next = request.query_params.get('next')
        if not next:
            next = '/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        return Response({
            'login_url': login_url
        })


















