from django import forms
from . import models
from zawody.models import Zawody, Turniej
from account.models import Account
from wyniki.models import Wyniki, Ustawienia
from django.core.exceptions import ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField
from django.forms.models import inlineformset_factory



class WynikiModelForm(forms.ModelForm):

    CHOICE= (
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')
    )
    # X = forms.CharField(widget=forms.Select(choices=CHOICE))
    X = forms.CharField()
    Xx = forms.CharField()
    dziewiec = forms.CharField()
    osiem = forms.CharField()
    siedem = forms.CharField()
    szesc = forms.CharField()
    piec = forms.CharField()
    cztery = forms.CharField()
    trzy = forms.CharField()
    dwa = forms.CharField()
    jeden = forms.CharField()
    kara_punktowa = forms.CharField()
    class Meta:
        model = Wyniki
        fields = ['X', 'Xx', 'dziewiec', 'osiem', 'siedem', 'szesc', 'piec', 'cztery', 'trzy', 'dwa', 'jeden','kara', 'kara_punktowa', 'edited_by_sedzia']

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean
        self.cleaned_data['edited_by_sedzia'] = 1
        if self.cleaned_data['kara_punktowa'] == None:
            self.cleaned_data['kara_punktowa'] = 0
        

    def __init__(self, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        strzaly = kwargs.pop('strzaly', None)                       #możliwe wyniki strzałów

        KARA_CHOICES = (
            ('BRAK', 'BRAK'),
            ('DNF', 'DNF'),
            ('DNS', 'DNS'),
            ('DSQ', 'DSQ'),
            ('PK', 'PK'),
            
        )
        super(WynikiModelForm, self).__init__(*args, **kwargs)
        self.fields['edited_by_sedzia'].widget = HiddenInput()


        self.fields["X"] = forms.CharField() 
        self.fields["Xx"] = forms.CharField(label='10') 
        self.fields["dziewiec"] = forms.CharField(label='9') 
        self.fields["osiem"] = forms.CharField(label='8') 
        self.fields["siedem"] = forms.CharField(label='7') 
        self.fields["szesc"] = forms.CharField(label='6') 
        self.fields["piec"] = forms.CharField(label='5') 
        self.fields["cztery"] = forms.CharField(label='4') 
        self.fields["trzy"] = forms.CharField(label='3') 
        self.fields["dwa"] = forms.CharField(label='2') 
        self.fields["jeden"] = forms.CharField(label='1') 
        self.fields["kara_punktowa"] = forms.CharField(label='Kara punktowa') 
        self.fields["kara"] = forms.ChoiceField(choices = KARA_CHOICES) 

class RejestracjaModelForm(forms.ModelForm):
    class Meta:
        model = Wyniki
        fields = (
            'zawody',
            'zawodnik',
            'bron_klubowa',
            'amunicja_klubowa',
            )

    def clean(self):
        cleaned_data = super().clean()
        #sprawdzam czy zawodnik nie jest już przypisany do danej konkurencji
        if not cleaned_data.get('zawody'):
            raise ValidationError('')
        wybrane_zawody = cleaned_data.get('zawody').id                                                                                                          
        wybrany_zawodnik = cleaned_data.get('zawodnik').id                                                                                                       
        zawodnik_juz_zarejestrowany = Wyniki.objects.filter(zawody=wybrane_zawody, zawodnik=wybrany_zawodnik)
        if zawodnik_juz_zarejestrowany:                                                                               
            raise ValidationError("Jesteś już zarejestrowany na te zawody")
            #formularz jest czyszczony więc ustawiam wartość początkową w polu zawodnik na tego zawodnika, który próbuje się zarejestrować
            self.fields['zawodnik'] =wybrany_zawodnik



    def __init__(self, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        #kwargs podwawane są z views.py
        user = kwargs.pop('user', None)
        pk = kwargs.pop('pk', None)
        super(RejestracjaModelForm, self).__init__(*args, **kwargs)
        self.fields['zawody'].queryset = Zawody.objects.filter(turniej__id=pk)
        self.fields['zawodnik'].queryset = Account.objects.all().order_by('nazwisko')

        #w zmiennej user podawana jest 1 jeśli user wywołujący formularz to rts (patrz plik views.py). Wtedy taki user może wybrać zawodnika, którego chce zarejestrować
        if not user:
            self.fields['zawodnik'].widget = HiddenInput()


class TurniejModelForm(forms.ModelForm):
    class Meta:
        model = Turniej
        fields = (
            'nazwa',
            'rejestracja',
            'klasyfikacja_generalna',
            )

ModuleFormSet = inlineformset_factory(Account,
                                      Wyniki,
                                      fields=['oplata', 'bron_klubowa', 'amunicja_klubowa',],
                                      extra=0,
                                      can_delete=False,
                                      labels = {'oplata': 'Opłata',}
                                      )

