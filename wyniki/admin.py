from django.contrib import admin
from account.models import Account
from wyniki.models import Wyniki, Ustawienia

# Register your models here.
@admin.register(Wyniki)
class WynikiAdmin(admin.ModelAdmin):
	list_display = ('slug', 'zawody', 'zawodnik','oplata', 'X', 'Xx', 'dziewiec', 'osiem', 'siedem', 'szesc', 'piec', 'cztery', 'trzy', 'dwa', 'jeden', 'wynik','result', 'kara_punktowa')
	search_fields = ('zawody', 'zawodnik')

# admin.site.register(Account, WynikiAdmin)

@admin.register(Ustawienia)
class UstawieniaAdmin(admin.ModelAdmin):
	list_display = ('nazwa','ustawienie')
	search_fields = ('nazwa','ustawienie')