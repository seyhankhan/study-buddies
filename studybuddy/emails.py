from os import environ

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendAt

IGNORE_TIMESTAMPS = True

def Email(to, templateID, templateData, timestamp=None):
	email = Mail(
		from_email=environ.get("SHS_EMAIL"),
		to_emails=to
	)
	# pass custom values for our HTML placeholders
	email.template_id = templateID
	email.dynamic_template_data = templateData

	if timestamp and not IGNORE_TIMESTAMPS:
		print(to, timestamp)
		email.send_at = SendAt(timestamp)
	
	return email


def sendEmail(email, client=SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))):
	try:
		response = client.send(email)
		print("Sent to:", email.from_email)
		print("Status Code:", response.status_code)
		print("Body:", response.body)
		print("Headers:\n", response.headers)
		return "SENT"
	except Exception as e:
		print(e)
		return "ERROR"


def sendEmails(emails):
	client = SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))
	for email in emails:
		sendEmail(email, client)
	print(len(emails), "emails sent")