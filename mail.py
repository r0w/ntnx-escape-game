import sys
import http.client
import json
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


if len(sys.argv) != 4 and len(sys.argv) != 5:
    print("Usage: mail.py <recipient email> <title> <template name> <Optional user_id>")
    exit(1)
else:
    recipient = sys.argv[1]
    title = sys.argv[2]
    templateName = sys.argv[3]
    if len(sys.argv) == 5:
        user_id = sys.argv[4]

file = open("email_templates/" + templateName, "r")
html_content = file.read()

# Update Content if {ID} are in the email content
if "{ID}" in html_content:
    html_content = html_content.replace("{ID}", f"{int(user_id):02d}")

# Send the email via Mailtrap API
conn = http.client.HTTPSConnection("send.api.mailtrap.io")

payload = {
    "to": [
        {
            "email": recipient,
        }
    ],
    "from": {
        "email": "ntnx-escapegame@ntnxlab.com",
        "name": "Nutanix Cloud Operations Command Center - Escape Game",
    },
    "subject": title,
    "html": html_content,
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Api-Token": "{MAIL_TOKEN}",
}

conn.request("POST", "/api/send", json.dumps(payload), headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
