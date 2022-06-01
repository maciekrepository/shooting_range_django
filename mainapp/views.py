from django.shortcuts import render
from zawody.models import Turniej

def home_screen_view(request, pk):
	context = {}
	context['pk'] = pk
	context['nazwa_turnieju'] = nazwa_turnieju(pk)
	return render(request, "mainapp/home.html", context)


def nazwa_turnieju(arg):
	nazwa = Turniej.objects.filter(id=arg).values_list('nazwa')
	nazwa_flat = []
	for i in nazwa:
		nazwa_flat.append(i)
	nazwa_str = ''.join(nazwa_flat[0])

	return nazwa_str