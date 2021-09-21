############ Seyhan Van Khan
############ Sex Homework Society Study Buddies
############ auto match people up every month uniquely according to chosen genders and monthly prompts
############ September 2021

from django.shortcuts import redirect, render

from .forms import JoinForm
from .models import Customer

#################################### INDEX ####################################

def index(request):
	return redirect("https://www.sexhomeworksociety.com/Sex Homework Society.pdf#page=2")

#################################### JOIN #####################################

def joinSuccess(request):
	return render(request, 'studybuddy/join-success.html')


def join(request):
	if not request.GET.get('user'):
		return render(request, 'studybuddy/error.html', {
			'error': "no user inputted",
		})

	try:
		customers = Customer()
		customer = customers.get(request.GET.get('user'))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render(request, 'studybuddy/error.html', {
				"error": "cant find this record",
			})
		else:
			raise(e)
	
	if request.method == "GET":
		form = JoinForm()
		return render(request, 'studybuddy/join.html', {
			"form": form,
			'name': customer['fields']['First Name'] + ' ' + customer['fields']['Last Name'],
			'email': customer['fields']['Email-test'],
			"recordID": customer['id'],
		})

	# POST
	else:
		form = JoinForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data['gendersToPairWith'])
			customers.update(customer['id'], {
				'Gender': form.cleaned_data['gender'],
				'Genders To Pair With': form.cleaned_data['gendersToPairWith'],
				'Study Buddy': True,
			})
			return redirect('join-success')
		else:
			print(form.errors)
			return render(request, "studybuddy/error.html")

################################### OPT OUT ###################################

def optout(request):
	if not request.GET.get('user'):
		return render(request, 'studybuddy/error.html', {
			'error': "no user inputted"
		})

	try:
		customers = Customer()
		customer = customers.get(request.GET.get('user'))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render(request, 'studybuddy/error.html', {
				"error": "cant find this record",
			})
		else:
			raise(e)
	
	customers.update(customer['id'], {
		'Study Buddy': False,
	})
	return render(request, 'studybuddy/optout.html', {
		"name": customer['fields']['First Name'],
		"recordID": customer['id'],
	})

################################### RE PAIR ###################################

def rePair(request):
	if not request.GET.get('user'):
		return render(request, 'studybuddy/error.html', {
			'error': "no user given"
		})

	try:
		customers = Customer()
		customer = customers.get(request.GET.get('user'))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render(request, 'studybuddy/error.html', {
				"error": "cant find this record",
			})
		else:
			raise(e)
	
	if request.method == 'GET':
		return render(request, 'studybuddy/re-pair.html', {
			"name": customer['fields']['First Name'],
			"recordID": customer['id'],
		})
	# POST
	else:
		customers.update(customer['id'], {
			'To be re-paired': True,
		})
