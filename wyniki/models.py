from django.core.exceptions import ValidationError
from django.db import models
from account.models import Account
from zawody.models import Zawody
class Wyniki(models.Model):
	# zawody = models.CharField(max_length=30)
	KARA_CHOICES = (
		('BRAK', 'BRAK'),
		('DNF', 'DNF'),
		('DNS', 'DNS'),
		('DSQ', 'DSQ'),
		('PK', 'PK'),
		
	)


	slug 		= models.SlugField(default=0)
	zawody 		= models.ForeignKey(Zawody, on_delete=models.CASCADE, verbose_name='konkurencja')
	zawodnik 	= models.ForeignKey(Account, on_delete=models.CASCADE)
	X			=models.IntegerField(blank=True, null=False, default=0)
	Xx			=models.IntegerField(blank=True, null=False, default=0, verbose_name='10')
	dziewiec	=models.IntegerField(blank=True, null=False, default=0, verbose_name='9')
	osiem		=models.IntegerField(blank=True, null=False, default=0, verbose_name='8')
	siedem		=models.IntegerField(blank=True, null=False, default=0, verbose_name='7')
	szesc		=models.IntegerField(blank=True, null=False, default=0, verbose_name='6')
	piec		=models.IntegerField(blank=True, null=False, default=0, verbose_name='5')
	cztery		=models.IntegerField(blank=True, null=False, default=0, verbose_name='4')
	trzy		=models.IntegerField(blank=True, null=False, default=0, verbose_name='3')
	dwa			=models.IntegerField(blank=True, null=False, default=0, verbose_name='2')
	jeden		=models.IntegerField(blank=True, null=False, default=0, verbose_name='1')
	wynik 		=models.IntegerField(blank=True, default=0)
	result		=models.TextField(max_length=60, null=True, default='0')
	kara		=models.CharField(max_length=10, choices=KARA_CHOICES, default='BRAK')
	kara_punktowa = models.IntegerField(blank=True, null=False, default=0, verbose_name='Kara punktowa')
	oplata		= models.BooleanField(default=False)
	bron_klubowa		= models.BooleanField(default=False, verbose_name='Broń klubowa')
	amunicja_klubowa		= models.BooleanField(default=False, verbose_name='Amunicja klubowa')
	edited_by_sedzia = models.BooleanField(default=False)
	# komunikat	=models.CharField(blank=True, max_length=100)

	class Meta:
		verbose_name_plural = "Wyniki"
# Create your models here.
	def save(self, *args, **kwargs):
		self.wynik = self.X*10 + self.Xx*10 + self.dziewiec*9 + self.osiem*8 + self.siedem*7 + self.szesc*6+ self.piec*5+ self.cztery*4+ self.trzy*3+ self.dwa*2+ self.jeden*1-self.kara_punktowa
		# self.slug = (self.zawodnik.username + str(self.zawody.id))
		# liczba_strzalow = self.X*10 + self.Xx*10 + self.dziewiec+ self.osiem + self.siedem + self.szesc+ self.piec+ self.cztery+ self.trzy+ self.dwa+ self.jeden
		# if liczba_strzalow < 10:
		# 	self.komunikat = ""
		self.result = str(self.X*10 + self.Xx*10 + self.dziewiec*9 + self.osiem*8 + self.siedem*7 + self.szesc*6+ self.piec*5+ self.cztery*4+ self.trzy*3+ self.dwa*2+ self.jeden*1-self.kara_punktowa)
		if self.kara not in ['BRAK', 'PK']:
			self.result = self.kara
			self.X=0
			self.Xx=0
			self.dziewiec=0
			self.osiem=0
			self.siedem=0
			self.szesc=0
			self.piec=0
			self.cztery=0
			self.trzy=0
			self.dwa=0
			self.jeden=0
			self.wynik=0
		if self.kara == 'PK':
			self.result = self.kara
			self.wynik = 0

		super(Wyniki, self).save(*args, **kwargs)

	def clean(self):
		# print(f'liczba strzalow {self.zawody.liczba_strzalow}')
		try:
			liczba_strzalow = self.zawody.liczba_strzalow
		except:
			raise ValidationError("Musisz wybrać konkurencję")

		mozliwe_wyniki = list(range(0,self.zawody.liczba_strzalow + 1))
		if (self.Xx not in mozliwe_wyniki):
			raise ValidationError({'Xx': f'Uzupełnij pole wartością od 0 do {liczba_strzalow}'})
		elif (self.X not in mozliwe_wyniki):
			raise ValidationError({'X': f'Uzupełnij pole wartością od 0 do {liczba_strzalow}'})
		elif (self.dziewiec not in mozliwe_wyniki):
			raise ValidationError({'dziewiec': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.osiem not in mozliwe_wyniki):
			raise ValidationError({'osiem': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.siedem not in mozliwe_wyniki):
			raise ValidationError({'siedem': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.szesc not in mozliwe_wyniki):
			raise ValidationError({'szesc': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.piec not in mozliwe_wyniki):
			raise ValidationError({'piec': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.cztery not in mozliwe_wyniki):
			raise ValidationError({'cztery': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.trzy not in mozliwe_wyniki):
			raise ValidationError({'trzy': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.dwa not in mozliwe_wyniki):
			raise ValidationError({'dwa': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif (self.jeden not in mozliwe_wyniki):
			raise ValidationError({'jeden': f'Uzupełnij  pole wartością od 0 do {liczba_strzalow}'})
		elif self.X+self.Xx+self.dziewiec+self.osiem+self.siedem+self.szesc+self.piec+self.cztery+self.trzy+self.dwa+self.jeden > liczba_strzalow:
			raise ValidationError(f'Maksymalna liczba strzałów w tej konkurencji to {liczba_strzalow}')


class Ustawienia(models.Model):
	nazwa = models.TextField()
	ustawienie = models.BooleanField(verbose_name='On/Off')

	class Meta:
		verbose_name_plural = "Ustawienia"