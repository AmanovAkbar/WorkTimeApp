from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models


# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.name


class OrganizationWorkTime(models.Model):
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"{self.organization.name}'s {self.name}"


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('User must have an email!')
        if not password:
            raise ValueError('User must have a password!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('admin', False)
        extra_fields.setdefault('staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_staffuser(self, email, password, **extra_fields):
        extra_fields.setdefault('admin', False)
        extra_fields.setdefault('staff', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('admin', True)
        extra_fields.setdefault('staff', True)

        if extra_fields.get('admin') is not True:
            raise ValueError('Superuser must have admin=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    organizations = models.ManyToManyField(Organization, blank=True)
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user;
    admin = models.BooleanField(default=False)  # a superuser
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-id']

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.email}'

    @staticmethod
    def has_perm(perm, obj=None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def has_module_perms(app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        # "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        # "Is the user active?"
        return self.active


class WorkTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='userworktime')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s worktime at {self.organization}"

    class Meta:
        ordering = ['created_at']