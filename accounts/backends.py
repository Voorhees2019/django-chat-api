from .models import User


class EmailOrUsernameModelBackend(object):
    """
    Authentication with either a username or an email address.
    """

    def authenticate(self, request, username=None, password=None):
        if "@" in username:
            kwargs = {"email": username}
        else:
            kwargs = {"username": username}

        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
