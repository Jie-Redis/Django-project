from django.contrib.auth.backends import ModelBackend
import re
from users.models import Users
from django.db.models import Q
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


def get_username_mobile(account):
    try:
        if re.match(r'^1[3-9]\d{9}', account):
            user = Users.objects.get(mobile=account)
        else:
            user = Users.objects.get(username=account)
    except:
        return None
    else:
        return user


class Usermobile(ModelBackend):
    '''重写该方法'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        '''

        :param request:
        :param username: 手机号或者用户名
        :param password: 密码 明文
        :param kwargs: 额外参数
        :return: user
        '''
        # try:
        #     if re.match(r'^1[3-9]\d{9}',username):
        #         user = Users.objects.get(mobile=username)
        #     else:
        #         user = Users.bojects.get(username=username)
        # except:
        #     return None
        # else:
        #     return user
        user = get_username_mobile(username)
        if user and user.check_password(password):
            return user
        else:
            return None


class UsernamemobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Users.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 序列化操作
def generate_token(user):
    # 创建一个序列化对象
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600 * 24)
    # 要进行序列化的对象
    data = {"user_id": user.id, "user_email": user.email}
    # 进行序列化
    try:
        token = s.dumps(data)
    except Exception as e:
        return None
    else:
        return settings.EMAIL_VERIFY_URL + "?token=" + token.decode()


# 去序列化
def check_token(token):
    # 创建一个序列化对象
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600 * 24)
    # 去序列化
    try:
        data = s.loads(token)
    except Exception as e:
        return None
    else:
        user_id = data.get("user_id")
        user_email = data.get("user_email")
        try:
            user = Users.objects.get(id=user_id, email=user_email)
        except Exception as e:
            return None
        else:
            return user
