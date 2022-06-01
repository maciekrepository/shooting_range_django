from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account

class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address')

	class Meta:
		model = Account
		fields = ("email", "username", "imie", "nazwisko", "klub", "licencja", "password1", "password2", "rodo_accepted")

	def clean(self):
		#nawisko ma być zapisane wielkimi literami
		cleaned_data = super().clean()
		nazwisko = cleaned_data.get('nazwisko') 
		nazwisko = nazwisko.upper() 
		self.cleaned_data['nazwisko'] = nazwisko
		if self.cleaned_data['rodo_accepted'] != 1:
			raise forms.ValidationError('Musisz zaakceptować postanowienia RODO aby przejść dalej')

class RegistrationFormSedzia(UserCreationForm):
	email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address')

	class Meta:
		model = Account
		fields = ("email", "username", "imie", "nazwisko", "klasa_sedziego", "licencja_sedziego","licencja", "is_sedzia", "password1", "password2", "rodo_accepted")

	def clean(self):
		cleaned_data = super().clean()
		nazwisko = cleaned_data.get('nazwisko') 
		nazwisko = nazwisko.upper() 
		self.cleaned_data['nazwisko'] = nazwisko
		#domyślnie ustawiamy 1 w polu is_sedzia. Propertka is_sedzzia i tak nie jest wyświetlana, sprawdź w htmlce
		self.cleaned_data['is_sedzia'] = 1
		if self.cleaned_data['rodo_accepted'] != 1:
			raise forms.ValidationError('Musisz zaakceptować postanowienia RODO aby przejść dalej')


class AccountAuthenticationForm(forms.ModelForm):
	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')
		
	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")

class AccountModelForm(forms.ModelForm):
	imie	 = forms.CharField(widget=forms.TextInput())
	nazwisko = forms.CharField(widget=forms.TextInput())
	licencja = forms.CharField(required=False,widget=forms.TextInput())
	klub	 = forms.CharField(required=False,widget=forms.TextInput())
	class Meta:
		model = Account
		fields = (
			'email',
			'username',
			'imie',
			'nazwisko',
			'licencja',
			'klub',
			'rts'
			)
	def clean(self):
		cleaned_data = super().clean()
		nazwisko = cleaned_data.get('nazwisko') 
		nazwisko = nazwisko.upper() 
		self.cleaned_data['nazwisko'] = nazwisko

class RodoModelForm(forms.ModelForm):
	class Meta:
		model = Account
		fields = (
			'rodo_accepted',
			)
		labels = {'rodo_accepted': 'Akceptuj'}

	def clean(self):
		data = self.cleaned_data
		if data['rodo_accepted'] != 1:
			raise forms.ValidationError('Musisz zaakceptować postanowienia RODO aby przejść dalej')




class AccountModelFormPersonal(forms.ModelForm):
	imie	 = forms.CharField(widget=forms.TextInput())
	nazwisko = forms.CharField(widget=forms.TextInput())
	licencja = forms.CharField(required=False,widget=forms.TextInput())
	klub	 = forms.CharField(required=False,widget=forms.TextInput())
	class Meta:
		model = Account
		fields = (
			'email',
			'username',
			'imie',
			'nazwisko',
			'licencja',
			'klub',
			)
	def clean(self):
		cleaned_data = super().clean()
		nazwisko = cleaned_data.get('nazwisko') 
		nazwisko = nazwisko.upper() 
		self.cleaned_data['nazwisko'] = nazwisko

class SedziaModelForm(forms.ModelForm):
	imie	 = forms.CharField(widget=forms.TextInput())
	nazwisko = forms.CharField(widget=forms.TextInput())
	licencja_sedziego = forms.CharField(required=False,widget=forms.TextInput())
	klasa_sedziego	 = forms.CharField(required=False,widget=forms.TextInput())
	licencja	 = forms.CharField(required=False,widget=forms.TextInput())
	klub	 = forms.CharField(required=False,widget=forms.TextInput())
	class Meta:
		model = Account
		fields = (
			'email',
			'username',
			'imie',
			'nazwisko',
			'licencja_sedziego',
			'klasa_sedziego',
			'licencja',
			'klub',
			)
	def clean(self):
		cleaned_data = super().clean()
		nazwisko = cleaned_data.get('nazwisko') 
		nazwisko = nazwisko.upper() 
		self.cleaned_data['nazwisko'] = nazwisko