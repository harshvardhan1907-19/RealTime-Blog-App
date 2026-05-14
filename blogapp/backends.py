from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
        Authenticate user using either username Or email
    """

    def authenticate(self, request, username = None, password = None, **kwargs):
        try:
            # Try to find user by username Or email
            user = User.objects.get(
                    Q(username__iexact=username) | Q(email__iexact=username)
                    # What is __iexact?
                    # Case-insensitive exact match
                )
        except User.DoesNotExist:
            return None
        
        # check password
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None