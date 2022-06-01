from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from zawody.models import Zawody
# Create your models here.

class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("Users must have mail address")
		if not username:
			raise ValueError("Users must have mail username")

		user = self.model(
				email=self.normalize_email(email),
				username=username,
			)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
				email=self.normalize_email(email),
				password = password,
				username=username,
			)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user




class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True, null=False)
	username 				= models.CharField(max_length=30, unique=True)
	imie					=models.TextField(max_length=60, null=False)
	nazwisko				=models.TextField(max_length=60, null=False)	
	licencja				=models.TextField(max_length=60, verbose_name='Numer licencji', blank=True, null=True)
	licencja_sedziego		=models.TextField(max_length=60, verbose_name='Numer licencji sędziego', blank=True, null=True)
	klub					=models.TextField(max_length=60,  blank=True, null=True)
	klasa_sedziego			=models.TextField(max_length=60, verbose_name='Klasa sędziego', blank=True, null=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	is_sedzia				= models.BooleanField(default=False)
	# paid					= models.BooleanField(default=False)
	rts						= models.BooleanField(default=False)
	rodo_accepted			= models.BooleanField(default=False)
	# first_name

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]

	objects = MyAccountManager();

	def __str__(self):
		return (self.nazwisko+' '+self.imie)

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True


