from os import environ

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendAt

from constants import DEBUG_MODE
from pairs import getUniquePairs

##################################### EMAIL ####################################


def Email(to, templateVariables, templateID, timestamp=None):
  email = Mail(
      from_email=environ.get("SHS_EMAIL"),
      to_emails=to
  )
  # pass custom values for our HTML placeholders
  email.dynamic_template_data = templateVariables
  email.template_id = templateID

  if timestamp and not DEBUG_MODE:
    print(to, timestamp)
    email.send_at = SendAt(timestamp)
  return email


def sendEmails(emails):
  sg = SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))
  for email in emails:
    try:
      response = sg.send(email)
      print("Sent to:", email.from_email)
      print("Status Code:", response.status_code)
      print("Body:", response.body)
      print("Headers:\n", response.headers)
    except Exception as e:
      print(e)

  print(len(emails), "emails sent")


def sendEmail(email):
  try:
    sg = SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))
    response = sg.send(email)
    print("Sent to:", email.from_email)
    print("Status Code:", response.status_code)
    print("Body:", response.body)
    print("Headers:\n", response.headers)
    return "SENT"
  except Exception as e:
    print(e)
    return "ERROR"


#################################### pairs ####################################


def sendPairsEmails():
  pairs = getUniquePairs()
  emails = []
  for pair in pairs:
    for buddy in pair:
      emails.append(Email(
				to=buddy['fields']['Email-test'],
				templateVariables={
					"name1": pair[0]['fields']['First Name'],
					"name2": pair[1]['fields']['First Name'],
					"email1": pair[0]['fields']['Email-test'],
					"email2": pair[1]['fields']['Email-test'],
					"recordID": buddy['id'],
				},
				templateID=environ.get("SENDGRID_SHS_MONTHLYSTUDYBUDDY_TEMPLATEID"),
      ))
  print(emails)
  sendEmail(emails[0])
	
sendPairsEmails()