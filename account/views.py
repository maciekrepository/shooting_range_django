from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, RegistrationFormSedzia, AccountAuthenticationForm, AccountModelForm, SedziaModelForm, AccountModelFormPersonal, RodoModelForm
from django.views.generic import ListView, UpdateView, DeleteView
from .models import Account
from zawody.models import Turniej
from django.contrib.auth import views as auth_views
from shootingrange import settings
import urllib
import json
import urllib.request


def nazwa_turnieju(arg):
	nazwa = Turniej.objects.filter(id=arg).values_list('nazwa')
	nazwa_flat = []
	for i in nazwa:
		nazwa_flat.append(i)
	nazwa_str = ''.join(nazwa_flat[0])

	return nazwa_str


def registration_form(request, pk):
	context={}
	context['pk'] = pk
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	if request.POST:
		form=RegistrationForm(request.POST)
		if form.is_valid():
			# print('jest is valid')
			recaptcha_response = request.POST.get('g-recaptcha-response')
			url = 'https://www.google.com/recaptcha/api/siteverify'
			values = {'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,'response': recaptcha_response}
			data = urllib.parse.urlencode(values).encode()
			req =  urllib.request.Request(url, data=data)
			response = urllib.request.urlopen(req)
			result = json.loads(response.read().decode())
			if result['success']:
				# print('jest success')
				form.save()
				messages.success(request, 'New comment added with success!')
				email = form.cleaned_data.get('email')
				raw_password = form.cleaned_data.get('password1')
				account = authenticate(email=email, password=raw_password)
				login(request, account)
				return redirect('home', pk)
			else:
				# print(' nie ma success')
				messages.error(request, 'Invalid reCAPTCHA. Please try again.')
		else:
			context['registration_form'] = form
	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)

def registration_form_sedzia(request, pk):
	context={}
	context['pk'] = pk
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	if request.POST:
		form=RegistrationFormSedzia(request.POST)
		if form.is_valid():
			print('jest is valid')
			recaptcha_response = request.POST.get('g-recaptcha-response')
			url = 'https://www.google.com/recaptcha/api/siteverify'
			values = {'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,'response': recaptcha_response}
			data = urllib.parse.urlencode(values).encode()
			req =  urllib.request.Request(url, data=data)
			response = urllib.request.urlopen(req)
			result = json.loads(response.read().decode())
			if result['success']:
				print('jest success')
				form.save()
				messages.success(request, 'New comment added with success!')
				email = form.cleaned_data.get('email')
				raw_password = form.cleaned_data.get('password1')
				account = authenticate(email=email, password=raw_password)
				login(request, account)
				return redirect('home', pk)
			else:
				print('lipa')
				messages.error(request, 'Invalid reCAPTCHA. Please try again.')
		else:
			context['registration_form'] = form
	else:
		form = RegistrationFormSedzia()
		context['registration_form'] = form
	return render(request, 'account/register_sedzia.html', context)
@login_required(login_url="/start/")
def registration_form_no_login(request,pk):
	context={}
	context['pk'] = pk
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	if request.POST:
		form=RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			return redirect('users', pk)
		else:
			context['registration_form'] = form
	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)

def logout_view(request, pk):
	logout(request)
	return redirect('home', pk)

def login_view(request, pk):
	context = {}
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	user = request.user
	if user.is_authenticated:
		return redirect("home")
	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				if user.rodo_accepted:
					return redirect("home", pk)
				else:
					return redirect("rodo_edit", user.id, pk)
	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form
	context['pk'] = pk
	return render(request, 'account/login.html', context)

def login_info(request, pk):
	return redirect('not_authorized')


class AccountUpdateView(LoginRequiredMixin, UpdateView):
	login_url = 'start'
	template_name = "account/account_update.html"
	form_class = AccountModelForm
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Account.objects.all()

	def get_success_url(self):
		return reverse("users", kwargs={'pk': self.kwargs['pk_turniej']})
		
	def form_valid(self, form):
		return super(AccountUpdateView,self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts:
				return super(AccountUpdateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')

class RodoUpdateView(LoginRequiredMixin, UpdateView):
	login_url = 'start'
	template_name = "account/rodo_update.html"
	form_class = RodoModelForm
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Account.objects.all()

	def get_success_url(self):
		return reverse("home", kwargs={'pk': self.kwargs['pk_turniej']})
		
	def form_valid(self, form):
		return super(RodoUpdateView,self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.id == self.kwargs['pk']:
				return super(RodoUpdateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')
			# pass


			
class AccountUpdateViewPersonal(LoginRequiredMixin, UpdateView):
	login_url = 'start'
	template_name = "account/account_update.html"
	form_class = AccountModelFormPersonal
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Account.objects.all()
		# return Account.objects.filter(id=request.user.id)

	def get_success_url(self):
		return reverse("home", kwargs={'pk': self.kwargs['pk_turniej']})
		
	def form_valid(self, form):
		return super(AccountUpdateViewPersonal,self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
	   # if request.user.is_sedzia or request.user.is_admin:
	   #     form_class = SedziaModelForm
		try:
			if request.user.id == self.kwargs['pk']:
				return super(AccountUpdateViewPersonal, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')

class SedziaUpdateView(LoginRequiredMixin, UpdateView):
	login_url = 'start'
	template_name = "account/account_update.html"
	form_class = SedziaModelForm
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Account.objects.all()

	def get_success_url(self):
		return reverse("home", kwargs={'pk': self.kwargs['pk_turniej']})
		
	def form_valid(self, form):
		return super(SedziaUpdateView,self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts or request.user.is_sedzia:
				return super(SedziaUpdateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
		  #  pass
			return redirect('not_authorized')


class AccountListView(LoginRequiredMixin, ListView):
	login_url = 'start'
	template_name = "account/account_list.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_queryset(self):
		return Account.objects.all().order_by('nazwisko')

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts:
				return super(AccountListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')



class AccountDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "account/account_delete.html"
	context_object_name = 'zawodnik'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Account.objects.all()

	def get_success_url(self):
		return reverse("users", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts:
				return super(AccountDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class PasswordResetViewNew(auth_views.PasswordResetView):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context
	def get_success_url(self):
		return reverse("password_reset_done", kwargs={'pk': self.kwargs['pk']})


class PasswordResetDoneViewNew(auth_views.PasswordResetDoneView):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

class PasswordResetConfirmViewNew(auth_views.PasswordResetConfirmView):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

class PasswordResetCompleteViewNew(auth_views.PasswordResetCompleteView):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context