import uuid
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, AbstractUser,
                                        PermissionsMixin, UnicodeUsernameValidator, Group)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from carrier_data_tool.base_models import BaseModel


class UserManager(BaseUserManager):
    """
    Creating a manager for custom user model.
    """

    def _create_user(self, email: str, username: str, password: str = None, **kwargs):
        # if 'company' not in kwargs:
        #     raise ValueError()
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email)
,
            username=username,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str = None, username=None, password=None, **kwargs):
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email=email, username=username, password=password, **kwargs)

    def create_superuser(self, email, username, password, **kwargs):
        """
        Create and return a `User` with superuser permissions.
        """
        kwargs.setdefault('is_superuser', True)
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self._create_user(email=email, username=username, password=password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    A custom user class implementing a fully featured User model with
    admin-compliant permissions.

    Username, Email and password are required. Other fields are optional.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _('email address'),
        max_length=255,
    )
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    is_active = models.BooleanField(_('active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as active. '
                                                'Unselect this instead of deleting accounts.'
                                                ),
                                    )
    is_staff = models.BooleanField(_('staff status'),
                                   default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'),
                                   )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    # groups = None

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        """
        to set table name in database
        """
        verbose_name = _('user')
        verbose_name_plural = _('users')

