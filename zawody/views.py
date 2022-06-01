from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.shortcuts import reverse
from .forms import ZawodyModelForm, SedziaModelForm
from .models import Sedzia, Zawody, Turniej
# from wyniki.views import sedziowie_lista
from django.shortcuts import redirect
# from account.views import sedziowie_lista
from mainapp.views import nazwa_turnieju

# Create your views here.


class StronaStartowaListView(ListView):
	template_name = "zawody/turniej_lista.html"

	def get_queryset(self):
		return Turniej.objects.filter(rejestracja=True)


class ZawodyListView(LoginRequiredMixin, ListView):
	login_url = '/start/'
	template_name = "zawody/zawody_lista.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_queryset(self, **kwargs):
		return Zawody.objects.filter(turniej=self.kwargs['pk'])

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(ZawodyListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class ZawodyCreateView(LoginRequiredMixin, CreateView):
	login_url = 'start'
	template_name = "zawody/zawody_create.html"
	form_class = ZawodyModelForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_success_url(self):
		return reverse("zawody_lista", kwargs={'pk':self.kwargs['pk']})
		return super(ZawodyCreateView, self).form_valid(form)
	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(ZawodyCreateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect("not_authorized")


class ZawodyEditView(LoginRequiredMixin,UpdateView):
	login_url = 'start'
	template_name = "zawody/zawody_edit.html"
	form_class = ZawodyModelForm
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Zawody.objects.all()

	def get_success_url(self):
		return reverse("zawody_lista", kwargs={'pk':self.kwargs['pk_turniej']})
		return super(TurniejEditView, self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(ZawodyEditView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')



class ZawodyDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "zawody/zawody_delete.html"
	context_object_name = 'zawody'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Zawody.objects.all()

	def get_success_url(self):
		return reverse("zawody_lista", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(ZawodyDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class SedziaCreateView(LoginRequiredMixin, CreateView):
	login_url = 'start'
	template_name = "zawody/sedzia_create.html"
	form_class = SedziaModelForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_success_url(self):
		return reverse("sedzia_lista", kwargs={'pk': self.kwargs['pk']})
		return super(SedziaCreateView, self).form_valid(form)

	def get_form_kwargs(self):
		kwargs = super(SedziaCreateView, self).get_form_kwargs()
		zawody_pk = self.kwargs['pk']
		kwargs.update({'zawody_pk': zawody_pk})
		return kwargs

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(SedziaCreateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')
			# pass

class SedziaListView(LoginRequiredMixin, ListView):
	login_url = 'start'
	template_name = "zawody/sedzia_lista.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		# context['rts_lista'] = rts_lista()
		return context

	def get_queryset(self):
		return Sedzia.objects.filter(zawody__turniej__id=self.kwargs['pk']).order_by('zawody')

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				print(request.user.id)
				return super(SedziaListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class SedziaDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "zawody/sedzia_delete.html"
	context_object_name = 'sedzia'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		# context['rts_lista'] = rts_lista()
		return context

	def get_queryset(self):
		return Sedzia.objects.all()

	def get_success_url(self):
		return reverse("sedzia_lista", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(SedziaDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


