from django.db import models
from account.models import Account


class Turniej(models.Model):
	nazwa = models.CharField(max_length=30)
	rejestracja = models.BooleanField(default=True, verbose_name='Rejestracja')
	klasyfikacja_generalna = models.BooleanField(default=True, verbose_name='Klasyfikacja generalna')

	def __str__(self):
		return self.nazwa

class Zawody(models.Model):
	nazwa = models.CharField(max_length=30)
	liczba_strzalow = models.IntegerField(default=10)
	turniej = models.ForeignKey(Turniej, on_delete=models.CASCADE, null=True)
	oplata_konkurencja = models.FloatField(default=0)
	oplata_bron = models.FloatField(default=0)
	oplata_amunicja = models.FloatField(default=0)

	def __str__(self):
		return self.nazwa
# Create your models here.
	class Meta:
		verbose_name_plural = "Zawody"


class Sedzia(models.Model):
	zawody 		= models.ForeignKey(Zawody, on_delete=models.CASCADE)
	sedzia 		= models.ForeignKey(Account, on_delete=models.CASCADE)


	class Meta:
		verbose_name_plural = "Sędziowie"