import json

from jwcrypto import jwk, jwt


class SecurityCell:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @property
    def __get_instance__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
        return self.__instance

    def generate_token(self, claim: dict, key, encrypt=True):
        """
        Create a signed token with the custom claims inserted
        :param claim: Dictionary with the data to be signed
        :param key: The key object generated
        :param encrypt:
        :return:
        """
        _key = {'k': key, 'kty': 'oct'}
        key = jwk.JWK(**_key)
        token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"},
                        claims=claim)

        if encrypt:
            token.make_encrypted_token(key)
        else:
            token.make_signed_token(key)

        return token.serialize()

    def verify_token(self, token, key):
        key = jwk.JWK(**key)
        token = u''+token
        ET = jwt.JWT(key=key, jwt=token)
        return json.loads(ET.claims)
