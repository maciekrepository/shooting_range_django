from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from wyniki.models import Wyniki
from zawody.models import Sedzia, Zawody
from account.models import Account
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import forms
from django.contrib.auth.decorators import login_required
import datetime
import xlwt
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .forms import WynikiModelForm, RejestracjaModelForm, TurniejModelForm, ModuleFormSet 
from zawody.models import Turniej
from mainapp.views import nazwa_turnieju
from django.db.models import Count, Sum



@csrf_exempt
@login_required(login_url="/start/")
def wyniki_edycja(request, pk):
	if request.user.is_sedzia:
		context = {}
		context['pk'] = pk
		context['nazwa_turnieju'] = nazwa_turnieju(pk)
		turniej = Turniej.objects.filter(id=pk).values_list('id', flat=True)
		turniej_id = turniej[0]

		#sprawdzam konkurencje przypisane do turnieju
		zawody_turnieju = Zawody.objects.filter(turniej=turniej_id).values_list('id', flat=True)
		zawody_turnieju_id = []
		for i in zawody_turnieju:
			zawody_turnieju_id.append(i)

		#sprawdzamy użytkownika ktory jest zalogowany
		user_id = request.user.id 					
		#sprawdzamy do jakich zawodow jest przyporzadkowany zalogowany user															
		powiazane_zawody = Sedzia.objects.filter(sedzia__id = user_id).values_list('zawody', flat=True)			
		powiazane_zawody_lista = []																				
		for i in powiazane_zawody:
			if i in zawody_turnieju_id:
				powiazane_zawody_lista.append(i)

		#zapisujemy w liście wyniki wyniki wszystkich zawodników dla poszczególnych zawodów
		powiazane_zawody_lista.sort()
		wyniki = []																			
		for i in powiazane_zawody_lista:
			wynik = Wyniki.objects.filter(zawody = i).order_by('zawodnik__nazwisko')
			#do listy wyniki mają trafiać tylko te wyniki, które dotyczą konkretnego turnieju
			#gdyby nie było dodatkowego filtrowania pojawiały by się błędy w przypadku gdy jedna konkurencja występowałaby w wielu turniejach
			wyniki.append(wynik.filter(zawody__turniej=pk, oplata=1))

		#zapisujemy w liście zawody_nazwa nazwy zawodów, z którymi powiązany jest sędzia
		zawody_nazwa = []
		nazwy_zawodow = Zawody.objects.filter(id__in=powiazane_zawody_lista).values_list('nazwa', flat=True)
		#do listy zawody_nazwa mają trafiać tylko te wyniki, które dotyczą konkretnego turnieju
		#gdyby nie było dodatkowego filtrowania pojawiały by się błędy w przypadku gdy jedna konkurencja występowałaby w wielu turniejach
		nazwy_zawodow = nazwy_zawodow.filter(turniej=pk)
		for i in nazwy_zawodow:
			zawody_nazwa.append(i)
		context['wyniki'] = wyniki
		context['zawody_nazwa'] = zawody_nazwa
		
		return render(request, 'wyniki/edytuj_wyniki.html', context)
	else:
		return redirect('not_authorized')

@login_required(login_url="/start/")
def wyniki(request, pk):
	context = {}
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	#robię listę 'zawody_lista' zawodów turnieju
	zawody = Zawody.objects.filter(turniej__id=pk).values_list('id', flat=True).order_by('id')
	zawody_lista = []
	for i in zawody:
		zawody_lista.append(i)
	#robię listę z nazwami zawodów 'zawody_nazwa' za pomocą listy 'zawody_lista' 
	zawody_nazwa_queryset = Zawody.objects.filter(turniej__id=pk).values_list('nazwa', flat=True).order_by('id')
	zawody_nazwa = []
	for i in zawody_nazwa_queryset:
		zawody_nazwa.append(i)

	wyniki = []
	sedziowie_queryset = []																						#robimy liste ktorej elementami beda wyniki poszczegolnych zawodow
	sedziowie = []
	for i in zawody_lista:
		wyniki.append(Wyniki.objects.filter(zawody = i, oplata=1).order_by('kara', '-wynik', '-X', '-Xx', '-dziewiec', '-osiem', '-siedem', '-szesc', '-piec', '-cztery', '-trzy', '-dwa', '-jeden'))
		sedziowie_queryset.append(Sedzia.objects.filter(zawody = i).values_list('sedzia__imie', 'sedzia__nazwisko'))
	for i in sedziowie_queryset:
		sedziowie.append(i)
	context['sedziowie'] = sedziowie
	klasyfikacja_generalna = Wyniki.objects.raw('select wyniki_wyniki.id, zawodnik_id, sum(X) as X, sum(Xx) as Xx,sum(dziewiec) as dziewiec, sum(osiem) as osiem,sum(siedem) as siedem , sum(szesc) as szesc, sum(piec) as piec, sum(cztery) as cztery, sum(trzy) as trzy, sum(dwa) as dwa, sum(jeden) as jeden, sum(wynik) as wynik from wyniki_wyniki inner join zawody_zawody on wyniki_wyniki.zawody_id = zawody_zawody.id where zawody_zawody.turniej_id = %s and oplata=1 and wyniki_wyniki.kara = %s group by zawodnik_id order by wynik desc, X desc, Xx desc, dziewiec desc, osiem desc, siedem DESC, szesc desc, piec desc, cztery desc, trzy desc, dwa desc, jeden desc', [pk, 'BRAK'])
	context['wyniki'] = wyniki
	context['zawody_nazwa'] = zawody_nazwa
	context['klasyfikacja_generalna'] = klasyfikacja_generalna
	klasyfikacja_generalna_display = Turniej.objects.filter(id=pk).values_list('klasyfikacja_generalna', flat=True)
	context['klasyfikacja_generalna_display'] = klasyfikacja_generalna_display[0]
	# print(f'klasyfikacja generalna:')
	context['pk'] = pk

	return render(request, 'wyniki/wyniki.html', context)




class RejestracjaNaZawodyView(LoginRequiredMixin, CreateView):
	login_url = 'start'
	template_name = "wyniki/rejestracja.html"
	form_class = RejestracjaModelForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		#sprawdzam czy rejestracja jest otwarta i podaję informację o tym w argumencie 'dodawanie_zawodnika'
		dodawanie_zawodnika = Turniej.objects.filter(id=self.kwargs['pk']).values_list("rejestracja", flat=True)
		rejestracja_otwarta = dodawanie_zawodnika[0]
		context['dodawanie_zawodnika'] = rejestracja_otwarta
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		# lista_zarejestrowanych = Wyniki.objects.filter(zawodnik__id = self.request.user.id).filter(zawody__turniej__id = self.kwargs['pk']).values_list("zawody__nazwa", flat=True)
		lista_zarejestrowanych = Wyniki.objects.filter(zawodnik__id = self.request.user.id).filter(zawody__turniej__id = self.kwargs['pk'])
		context['lista_zarejestrowanych'] = lista_zarejestrowanych
		suma_oplat = 0
		for i in lista_zarejestrowanych:
			suma_oplat += i.zawody.oplata_konkurencja
			if i.amunicja_klubowa:
				suma_oplat += i.zawody.oplata_amunicja
			if i.bron_klubowa:
				suma_oplat += i.zawody.oplata_bron

			# print(f'konkurencja: {i.zawody} amunicja_klubowa: {i.amunicja_klubowa}  cena: {i.zawody.oplata_amunicja}')
			# print(f'konkurencja: {i.zawody} broń klubowa: {i.bron_klubowa} cena: {i.zawody.oplata_bron} ')
		context['suma_oplat'] = suma_oplat
		return context

	def get_success_url(self):
		return reverse("rejestracja_na_zawody", kwargs={'pk': self.kwargs['pk']})
		return super(RejestracjaNaZawodyView, self).form_valid(form)

	def get_form_kwargs(self):
		kwargs = super(RejestracjaNaZawodyView, self).get_form_kwargs()
		kwargs.update({'user': self.request.user.rts})
		kwargs.update({'pk': self.kwargs['pk']})
		return kwargs

	def get_initial(self, *args, **kwargs):
		initial = super(RejestracjaNaZawodyView, self).get_initial()
		initial = initial.copy()
		initial['zawodnik'] = self.request.user
		return initial


class WynikUpdateView(LoginRequiredMixin, UpdateView):
	login_url = 'start'
	template_name = "wyniki/wyniki_edit.html"
	form_class = WynikiModelForm
	context_object_name = 'cont'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Wyniki.objects.all()

	def get_success_url(self):
		return reverse("wyniki_edycja", kwargs={'pk': self.kwargs['pk_turniej']})

	def form_valid(self, form):
		return super(WynikUpdateView,self).form_valid(form)

	def get_form_kwargs(self):
		kwargs = super(WynikUpdateView, self).get_form_kwargs()
		zawody = Wyniki.objects.filter(id = self.kwargs['pk']).values_list('zawody__id', flat=True)
		# print(f'zawody: {zawody[0]}')
		liczba_strzalow = Zawody.objects.filter(id = zawody[0]).values_list('liczba_strzalow', flat=True)
		liczba_strzalow_range = list(range(0,liczba_strzalow[0]+1))
		lista = []
		for i in liczba_strzalow_range:
			lista.append(tuple((i,i)))
		kwargs.update({'strzaly': lista})
		# kwargs.update({'is_sedzia_editing': self.request.user.is_sedzia and not self.request.user.rts})
		return kwargs


	def dispatch(self, request, *args, **kwargs):
		wynik_pk = self.kwargs.get('pk')
		wynik_edytowany = Wyniki.objects.filter(id = wynik_pk).values_list('edited_by_sedzia', flat=True)
		zawody_pk = Wyniki.objects.filter(id = wynik_pk).values_list('zawody__id', flat=True)
		zawody_pk_lista = []
		for i in zawody_pk:
			zawody_pk_lista.append(i)
		zawody_pk_lista = zawody_pk_lista[0]
		sedzia_pk = Sedzia.objects.filter(zawody__id = zawody_pk_lista).values_list('sedzia__id', flat=True)
		sedzia_pk_lista = []
		for i in sedzia_pk:
			sedzia_pk_lista.append(i)
		user_id=self.request.user.id
		sedzia_not_rts = self.request.user.is_sedzia and not self.request.user.rts
		if user_id in sedzia_pk_lista:
			if sedzia_not_rts and wynik_edytowany[0]:
				return redirect('not_authorized')
			else:
				return super(WynikUpdateView, self).dispatch(request, *args, **kwargs)
		else:
			return redirect('not_authorized')


def not_authorized(request):
	return render(request, 'wyniki/not_authorized.html')

@login_required(login_url="/start/")
def exportexcel(request, pk):
	if request.user.is_admin:
		response=HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename=Wyniki_' + str(datetime.datetime.now())+'.xls'
		wb = xlwt.Workbook(encoding='utf-8')

		zawody = Zawody.objects.filter(turniej__id=pk).values_list('nazwa', flat=True).order_by('id')
		ws = []
		for i in zawody:
			ws.append(wb.add_sheet(i))

		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold=True

		columns = ['Pozycja','Nazwisko','Imię', 'Klub', 'Suma']

		for col_num in range(len(columns)):
			for i in ws:
				i.write(row_num, col_num, columns[col_num], font_style)


		font_style = xlwt.XFStyle()
		zawody_id = Zawody.objects.filter(turniej__id=pk).values_list('id', flat=True).order_by('id')
		zawody_id_lista = []
		for i in zawody_id:
			zawody_id_lista.append(i)


		rows = []
		for count, i in enumerate(zawody_id_lista):
			rows.append(Wyniki.objects.filter(zawody__id = i, oplata = 1).values_list('zawodnik__nazwisko','zawodnik__imie', 'zawodnik__klub', 'wynik').order_by('-wynik', '-X', '-Xx', '-dziewiec', '-osiem', '-siedem', '-szesc', '-piec', '-cztery', '-trzy', '-dwa', '-jeden'))
			# queryset = Wyniki.objects.filter(zawody__id = i, oplata = 1).values_list('zawodnik__nazwisko','zawodnik__imie', 'zawodnik__klub', 'wynik').order_by('-wynik', '-X', '-Xx', '-dziewiec', '-osiem', '-siedem', '-szesc', '-piec', '-cztery', '-trzy', '-dwa', '-jeden')
			# items = zip(range(1,queryset.count()+1), queryset)


			# rows.append(items)

		# rows.append(Wyniki.objects.filter(zawody__turniej = pk, oplata = 1).values_list('zawodnik__nazwisko','zawodnik__imie', 'zawodnik__klub', 'X', 'Xx', 'dziewiec', 'osiem', 'siedem', 'szesc', 'piec', 'cztery', 'trzy', 'dwa', 'jeden', 'wynik', 'kara').order_by('-wynik', '-X', '-Xx', '-dziewiec', '-osiem', '-siedem', '-szesc', '-piec', '-cztery', '-trzy', '-dwa', '-jeden'))	
		generalka = Wyniki.objects.raw('select account_account.nazwisko, account_account.imie, account_account.klub, sum(wynik) as wynik, account_account.id from account_account inner join zawody_zawody on wyniki_wyniki.zawody_id = zawody_zawody.id inner join wyniki_wyniki on account_account.id=wyniki_wyniki.zawodnik_id where zawody_zawody.turniej_id = %s and oplata=1 and wyniki_wyniki.kara = %s group by account_account.id order by wynik desc, X desc, Xx desc, dziewiec desc, osiem desc, siedem DESC', [pk, 'BRAK'])
		# generalka = Wyniki.objects.raw('select wyniki_wyniki.id, zawodnik_id, sum(X) as X, sum(Xx) as Xx,sum(dziewiec) as dziewiec, sum(osiem) as osiem,sum(siedem) as siedem , sum(szesc) as szesc, sum(piec) as piec, sum(cztery) as cztery, sum(trzy) as trzy, sum(dwa) as dwa, sum(jeden) as jeden, sum(wynik) as wynik from wyniki_wyniki inner join zawody_zawody on wyniki_wyniki.zawody_id = zawody_zawody.id where zawody_zawody.turniej_id = %s and oplata=1 and wyniki_wyniki.kara = %s group by zawodnik_id order by wynik desc, X desc, Xx desc, dziewiec desc, osiem desc, siedem DESC', [pk, 'BRAK'])
		# rows.append(generalka)
		for x,y in enumerate(ws):
			row_num = 0
			for index, row in enumerate(rows[x], start=1):
				row_num +=1
				for col_num in range(len(row)+1):
					if col_num==0:
						y.write(row_num, col_num, index, font_style)
					else:
						y.write(row_num, col_num, str(row[col_num-1]), font_style)

		klasyfikacja_generalna_display = Turniej.objects.filter(id=pk).values_list('klasyfikacja_generalna', flat=True)
		if klasyfikacja_generalna_display[0] == 1:

			ws.append(wb.add_sheet("Klasyfikacja generalna"))
			columns = ['Pozycja','Nazwisko','Imię', 'Klub', 'Suma']
			row_num = 0
			font_style = xlwt.XFStyle()
			font_style.font.bold=True
			for col_num in range(len(columns)):
					ws[len(ws)-1].write(row_num, col_num, columns[col_num], font_style)

			font_style = xlwt.XFStyle()
			tab_generalka = len(ws)-1
			for i,y in enumerate(generalka):
				ws[tab_generalka].write(i+1,   0, i+1, font_style)
				ws[tab_generalka].write(i+1, 1, y.nazwisko, font_style)
				ws[tab_generalka].write(i+1, 2, y.imie, font_style)
				ws[tab_generalka].write(i+1, 3, y.klub, font_style)
				ws[tab_generalka].write(i+1, 4, y.wynik, font_style)


		ws.append(wb.add_sheet("Sędziowie"))
		columns = ['Klasa', 'Nazwisko', 'Imię']
		row_num=0
		font_style = xlwt.XFStyle()
		font_style.font.bold=True
		tab_sedziowie = len(ws)-1

		for col_num in range(len(columns)):
			ws[tab_sedziowie].write(row_num, col_num, columns[col_num], font_style)



		font_style = xlwt.XFStyle()
		sedziowie = Sedzia.objects.filter(zawody__id__in = zawody_id_lista).values_list('sedzia__klasa_sedziego', 'sedzia__nazwisko', 'sedzia__imie').distinct()
		print(sedziowie)
		for sedzia in sedziowie:
			row_num +=1
			for col_num in range(len(sedzia)):
				ws[tab_sedziowie].write(row_num, col_num, str(sedzia[col_num]), font_style)




		wb.save(response)

		return(response)

	else:
		return redirect('home')


class KonkurencjaDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "wyniki/konkurencja_delete.html"
	context_object_name = 'zawodnik'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Wyniki.objects.all()

	def get_success_url(self):
		return reverse("wyniki", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(KonkurencjaDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class TurniejListView(LoginRequiredMixin, ListView):
	login_url = 'start'
	template_name = "wyniki/turniej_list.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_queryset(self):
		return Turniej.objects.all()

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(TurniejListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')



class TurniejDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "wyniki/turniej_delete.html"
	context_object_name = 'turniej'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Turniej.objects.all()

	def get_success_url(self):
		return reverse("turnieje", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(TurniejDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')




class TurniejCreateView(LoginRequiredMixin, CreateView):
	login_url = 'start'
	template_name = "wyniki/turniej_create.html"
	form_class = TurniejModelForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_success_url(self):
		return reverse("turnieje", kwargs={'pk':self.kwargs['pk']})
		return super(TurniejListView, self).form_valid(form)
	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(TurniejCreateView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect("not_authorized")



class TurniejEditView(LoginRequiredMixin,UpdateView):
	login_url = 'start'
	template_name = "wyniki/turniej_edit.html"
	form_class = TurniejModelForm
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Turniej.objects.all()

	def get_success_url(self):
		return reverse("turnieje", kwargs={'pk':self.kwargs['pk_turniej']})
		return super(TurniejEditView, self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.is_admin:
				return super(TurniejEditView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')


class OplataListView(LoginRequiredMixin, ListView):
	login_url = 'start'
	template_name = "wyniki/oplata_list.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		return context

	def get_queryset(self):
		turniej_zawodnicy = Wyniki.objects.filter(zawody__turniej__id = self.kwargs['pk']).values_list('zawodnik__id')
		turniej_zawodnicy_id = []
		for i in turniej_zawodnicy:
			turniej_zawodnicy_id.append(i[0])
		turniej_zawodnicy_id_set = set(turniej_zawodnicy_id)
		o1 =  Account.objects.filter(id__in = turniej_zawodnicy_id_set).order_by('nazwisko')
		o2 =  Wyniki.objects.filter(zawodnik__id__in = turniej_zawodnicy_id_set, zawody__turniej__id = self.kwargs['pk']).values_list('zawodnik__id','zawodnik__email','zawody__nazwa').order_by('zawodnik__nazwisko')
		return [o1, o2]
		# return Account.objects.filter(id__in = turniej_zawodnicy_id_set).order_by('nazwisko')

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts or request.user.is_superuser:
				return super(OplataListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')
			# pass




class OplataUpdateView(LoginRequiredMixin, TemplateResponseMixin, View):
    login_url='start'
    template_name = 'wyniki/oplata_update.html'
    account = None

    def get_formset(self, data=None, turniej=1):
        return ModuleFormSet(instance=self.account,queryset=Wyniki.objects.filter(zawody__turniej__id=turniej),
                             data=data)

    def dispatch(self, request, pk, pk_turniej):
    	try:

    		if request.user.rts or request.user.is_superuser:
    			self.account = get_object_or_404(Account,
		                                        id=pk)
    			return super().dispatch(request, pk)
    		else:
    			return reverse('not_authorized')
    	except:
    		return redirect(reverse('not_authorized'))


    def get(self, request, *args, **kwargs):
        formset = self.get_formset(turniej=self.kwargs['pk_turniej'])
        return self.render_to_response({'account': self.account,
                                        'formset': formset,
                                        'pk': self.kwargs['pk_turniej'],
                                        'nazwa_turnieju': nazwa_turnieju(self.kwargs['pk_turniej'])})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST, turniej=self.kwargs['pk_turniej'])
        if formset.is_valid():
            formset.save()
            return redirect(reverse("oplata_list", kwargs={'pk': self.kwargs['pk_turniej']}))
        return self.render_to_response({'account': self.account,
                                        'formset': formset,
                                        'pk': self.kwargs['pk_turniej'],
                                        'nazwa_turnieju': nazwa_turnieju(self.kwargs['pk_turniej'])})



class UczestnikDeleteView(LoginRequiredMixin, DeleteView):
	login_url = 'start'
	template_name = "wyniki/uczestnik_delete.html"
	context_object_name = 'uczestnik'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk_turniej']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk_turniej'])
		return context

	def get_queryset(self):
		return Wyniki.objects.all()

	def get_success_url(self):
		return reverse("oplata_list", kwargs={'pk': self.kwargs['pk_turniej']})

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts:
				return super(UczestnikDeleteView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')




class BronAmunicjaListView(LoginRequiredMixin, ListView):
	login_url = 'start'
	template_name = "wyniki/bron_amunicja_list.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['nazwa_turnieju'] = nazwa_turnieju(self.kwargs['pk'])
		abr = (Wyniki.objects.filter(zawody__turniej__id = self.kwargs['pk']).values('zawody__nazwa').annotate(acount=Sum('amunicja_klubowa'), bcount=Sum('bron_klubowa')).order_by())
		context['abr'] = abr
		return context

	def get_queryset(self):
		return Wyniki.objects.filter(zawody__turniej__id = self.kwargs['pk']).order_by('zawody')

	def dispatch(self, request, *args, **kwargs):
		try:
			if request.user.rts or request.user.is_sedzia:
				return super(BronAmunicjaListView, self).dispatch(request, *args, **kwargs)
			else:
				return redirect('not_authorized')
		except:
			return redirect('not_authorized')
			# pass