from django import forms

GENDERS = [
	('Female', 'Female'),
	('Male', 'Male'),
	('Non-Binary', 'Non-Binary'),
]

class JoinForm(forms.Form):
	# name = forms.CharField(label='Name', max_length=100, required=False, disabled=True)
	# email = forms.CharField(label='Email', max_length=30, required=False, disabled=True)
	gender = forms.ChoiceField(label='Gender', widget=forms.RadioSelect, choices=GENDERS)
	gendersToPairWith = forms.MultipleChoiceField(label='Genders to pair with', widget=forms.CheckboxSelectMultiple, choices=GENDERS)
