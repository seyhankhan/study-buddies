from os import environ

from django.conf import settings
from pyairtable import Table


class Customer(Table):
  def __init__(self):
    super().__init__(
			environ.get('AIRTABLE_KEY'),
			environ.get('AIRTABLE_SHS_BASE'),
			'Seyhan test copy'# if settings.DEBUG else 'Customers'
		)

class Offering(Table):
  def __init__(self):
    super().__init__(
			environ.get('AIRTABLE_KEY'),
			environ.get('AIRTABLE_SHS_BASE'),
			'Offerings'
		)