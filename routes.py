############ Seyhan Van Khan
############ Sex Homework Society Study Buddies
############ auto match people up every month uniquely according to chosen genders and monthly prompts
############ September 2021

################################ IMPORT MODULES ################################


from json import dumps
log = lambda a: print(dumps(a, indent=2))
from os import environ

from flask import Flask, render_template, redirect, request, url_for
from pyairtable import Table
from pyairtable.formulas import match

from constants import CUSTOMERS_TABLE, DEBUG_MODE


################################### INIT APP ###################################


app = Flask(__name__)


##################################### INDEX ####################################


@app.route('/', methods=['GET'])
def index():
	return redirect('https://www.sexhomeworksociety.com/')


##################################### ERROR ####################################


@app.route('/error', methods=['GET'])
def error():
	return render_template('error.html')


################################# JOIN SUCCESS #################################


@app.route('/join-success', methods=['GET'])
def joinSuccess():
	return render_template('join-success.html')


##################################### JOIN #####################################


@app.route('/join', methods=['GET', 'POST'])
def join():
	if not request.args.get('user'):
		return render_template('error.html', error="no user inputted")

	try:
		customersTable = Table(
			environ.get("AIRTABLE_KEY"),
			environ.get("AIRTABLE_SHS_BASE"),
			CUSTOMERS_TABLE
		)
		customer = customersTable.get(request.args.get('user'))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render_template('error.html', error="cant find this record", description=e)
		else:
			raise(e)
	
	if request.method == "GET":
		email = customer['fields']['Email-test']
		endIndex = min(13, email.index('@') + 1)
		hiddenEmail = email[:endIndex] + '*' * 10
		# hiddenEmail[email.index('@')] = '@'

		return render_template(
			'join.html',
			recordID=customer['id'],
			name=customer['fields']['First Name'],
			email=hiddenEmail,
		)

	# POST
	else:
		customersTable.update(customer['id'], {
			'Gender': request.form['gender'],
			'Genders To Pair With': request.form.getlist('genders-to-pair-with'),
			'Study Buddy': True,
		})
		return redirect('join-success')	


################################### OPT OUT ###################################


@app.route('/optout', methods=['GET'])
def optout():
	if not request.args.get('user'):
		return render_template('error.html', error="no user inputted")

	try:
		customersTable = Table(
			environ.get("AIRTABLE_KEY"),
			environ.get("AIRTABLE_SHS_BASE"),
			CUSTOMERS_TABLE
		)
		customer = customersTable.get(request.args.get('user'))
	except Exception as e:
		if e.response.status_code == 404:
			print(e)
			return render_template('error.html', error="cant find this record", description=e)
		else:
			raise(e)
	
	customersTable.update(customer['id'], {
		'Study Buddy': False,
	})
	return render_template(
		'optout-success.html',
		name=customer['fields']['First Name'],
		recordID=customer['id'],
	)
	

################################# OTHER ROUTES #################################


@app.route('/<path:dummy>')
def fallback(dummy):
	return redirect(url_for('index'))


#################################### APP RUN ###################################


if __name__ == "__main__":
	app.run(debug=DEBUG_MODE)
