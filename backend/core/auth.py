import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
import settings
from starlette.status import HTTP_401_UNAUTHORIZED

# pyjwt: pip install pyjwt==2.10.1


from threading import Lock

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AuthHandler(metaclass=SingletonMeta):
    security = HTTPBearer()
    # Authorization: Bearer {token}

    secret = settings.JWT_SECRET_KEY

    def encode_access_token(self, user_id: int) -> str:
        exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        to_encode = dict(
            iss=user_id,
            exp=int(exp.timestamp())
        )
        return jwt.encode(to_encode, self.secret, algorithm='HS256')

    def decode_access_token(self, token):
        # ACCESS TOKEN：过期或不可用，统一返回401
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='登录已过期，请重新登录！')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Token不可用！')

    def auth_access_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """在需要登录的接口上以 Depends 使用，返回当前用户 id。"""
        return self.decode_access_token(auth.credentials)
