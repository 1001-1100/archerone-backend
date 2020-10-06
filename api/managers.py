from django.db import models

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, username, password=None):
        user = self.model(
            username=username,
            is_admin=False,
            is_administrator=False,
            is_superuser=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_staffuser(self, email, password=None):
    #     user = self.model(
    #         email=self.normalize_email(email),
    #         is_staff=True,
    #     )
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            password=password
        )
        user.is_admin=True
        user.is_administrator=True
        user.is_superuser=True
        user.save(using=self._db)
        return user