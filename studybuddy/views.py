############ Seyhan Van Khan
############ Sex Homework Society Study Buddies
############ auto match people up every month uniquely according to chosen genders and monthly prompts
############ September 2021

from datetime import datetime
from os import environ
from pytz import timezone

from django.shortcuts import redirect, render

from .forms import JoinForm
from .emails import Email, sendEmails
from .models import Customer


#################################### INDEX ####################################

def index(request):
	return redirect("https://www.sexhomeworksociety.com/Sex%20Homework%20Society.pdf#page=2")

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
	
	if customer['fields'].get('Study Buddy'):
		return render(request, 'studybuddy/error.html', {
			'error': "you've already registered",
		})
	
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
	
	if customer['fields']['Study Buddy']:
		pass
		# TODO - already opted out

	customers.update(customer['id'], {
		'Study Buddy': False,
	})
	return render(request, 'studybuddy/optout.html', {
		"name": customer['fields']['First Name'],
		"recordID": customer['id'],
	})

################################### RE PAIR ###################################

def rePair(request):
	# check link is all good
	if not (request.GET.get('user') and request.GET.get('deadline') and request.GET.get('pair1')):
		return render(request, 'studybuddy/error.html', {
			'error': "incomplete link, use link given in email"
		})

	# check if within deadline to re pair
	try:
		rePairDeadline = int(request.GET['deadline'])
		# try convert to date to see if its actually valid timestamp
		datetime.fromtimestamp(rePairDeadline)
	except (TypeError, ValueError) as e:
		print(e)
		return render(request, 'studybuddy/error.html', {
			'error': "incomplete link, use link given in email"
		})

	now = timezone('Europe/London').localize(datetime.now()).timestamp()
	if now > rePairDeadline:
		return render(request, 'studybuddy/error.html', {
			'error': "you're too late! re-pairing occurs 7 days after at 10am UK time",
		})

	# get data on the re-pairer & his pairs
	try:
		customers = Customer()
		customer = customers.get(request.GET['user'])
		pairs = [customers.get(request.GET['pair1'])]
		if request.GET.get('pair2'):
			pairs.append(customers.get(request.GET['pair2']))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render(request, 'studybuddy/error.html', {
				"error": "cant find this record",
			})
		else:
			raise(e)

	# user is not even a study buddy
	if not customer['fields'].get('Study Buddy'):
		return render(request, 'studybuddy/error.html', {
			'error': "you're not currently listed as a study buddy",
		})


	# if they already clicked the button and did this whole thing before
	if customer['fields'].get('Re-Pair'):
		return render(request, 'studybuddy/error.html', {
			'error': "we've already set you up for re-pair! Re-pairing occurs on the 8th, at 10am UK time",
		})
	# check if this guy even had pairs in airtable
	previousPairs = customer['fields'].get('Pairs')
	if not previousPairs:
		return render(request, 'studybuddy/error.html', {
			'error': "you have no pairs?",
		})

	# email all his pairs & tell em John decided to re-pair
	emails = []
	# for each of reporter's pairs
	for pair in pairs:
		# if this person already re-paired, no need for emailing & updating their list
		if pair['fields'].get('Re-Pair'):
			continue
		if pair['id'] not in previousPairs:
			return render(request, 'studybuddy/error.html', {
				'error': "these are not your pairs? did u use the correct email link?",
			})
		# remove the re-pairer (& other buddy) from this pair's list
		customers.update(pair['id'], {
			'Pairs': list(filter(
				lambda id: id not in pairs and id != customer['id'],
				pair['fields']['Pairs'],
			)),
		})

		# email pair he's too late & should be better next month
		emails.append(Email(
			to=pair['fields']['Email-test'],
			templateID=environ.get('SENDGRID_SHS_YOUR_PAIR_REPAIRED_TEMPLATEID'),
			templateData={
				'name': pair['fields']['First Name'],
				'rePairName': customer['fields']['First Name'],
			}
		))
	# remove pairs from customer's list
	# turn re-pair ON for this customer
	# save his/her pair so they don't get them for re-pair
	customers.update(customer['id'], {
		'Pairs': [id for id in customer['fields']['Pairs'] if id not in pairs],
		'Re-Pair': True,
		'Avoid for Re-Pair': [pair['id'] for pair in pairs],
	})

	sendEmails(emails)

	return render(request, 'studybuddy/re-pair.html', {
		"name": customer['fields']['First Name'],
	})
