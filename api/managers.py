from django.db import models

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None):
        user = self.model(
            email=self.normalize_email(email),
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

    def create_superuser(self, email, password=None):
        user = self.model(
            email=self.normalize_email(email),
            is_superuser=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user