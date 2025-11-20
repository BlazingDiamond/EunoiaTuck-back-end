from django.contrib.auth.backends import BaseBackend


from .models import User


class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Custom authentication backend to allow users to log in using their email address
# #though not certain if it works since im using a different system for auth now
