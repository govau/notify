"""

Revision ID: 0190_change_templates_to_dta
Revises: 0189_rename_notify_service
Create Date: 2018-07-11 13:47:36.370320

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0190_change_templates_to_dta'
down_revision = '0189_rename_notify_service'

templates = [{
    'id': "618185c6-3636-49cd-b7d2-6f6f5eb3bdde",
    'new_name': "Automated \"You’re now live\" message",
    'new_subject': "((service name)) is now live on Notify.gov.au",
    'new_content': """Hi ((name)),

((service name)) is now live on Notify.

You can send up to ((message limit)) messages per day.

As a live service, you’ll need to know who to contact if you have a question, or something goes wrong.

^To get email updates whenever there is a problem with Notify, it’s important that you subscribe to our system status page:
https://status.notify.gov.au

If our system status page shows a problem, then we’ve been alerted and are working on it – you don’t need to contact us.
#Problems or questions during office hours

Support times
Our office hours are 9:30am to 5:00pm, Monday to Friday.

Out-of-hours
During Alpha we do not provide out-of-hours support.

Thanks
Notify.gov.au team
""",
    'old_name': "Automated \"You''re now live\" message",
    'old_subject': "((service name)) is now live on GOV.AU Notify",
    'old_content': """Hi ((name)),

((service name)) is now live on GOV.AU Notify.

You can send up to ((message limit)) messages per day.

As a live service, you’ll need to know who to contact if you have a question, or something goes wrong.

^To get email updates whenever there is a problem with Notify, it’s important that you subscribe to our system status page:
https://status.notifications.service.gov.uk

If our system status page shows a problem, then we’ve been alerted and are working on it – you don’t need to contact us.
#Problems or questions during office hours

Our office hours are 9.30am to 5.30pm, Monday to Friday.

To report a problem or ask a question, go to the support page:
https://www.notifications.service.gov.uk/support

We’ll reply within 30 minutes whether you’re reporting a problem or just asking a question.

The team are also available to answer questions on the cross-government Slack channel:
https://ukgovernmentdigital.slack.com/messages/govuk-notify

#Problems or questions out of hours

We offer out of hours support for emergencies.

It’s only an emergency if:
*   no one in your team can log in
*   a ‘technical difficulties’ error appears when you try to upload a file
*   a 500 response code appears when you try to send messages using the API

If you have one of these emergencies, email details to:
ooh-gov-uk-notify-support@digital.cabinet-office.gov.uk

^Only use this email address for out of hours emergencies. Don’t share this address with people outside of your team.

We’ll get back to you within 30 minutes and give you hourly updates until the problem’s fixed.

For non-emergency problems or questions, use our support page and we’ll reply in office hours:
https://www.notifications.service.gov.uk/support
#Escalation for emergency problems

If we haven’t acknowledged an emergency problem you’ve reported within 30 minutes and you need to know what’s happening, you can escalate to:

or

Thanks
GOV.AU Notify team
"""
}, {
    'id': "eb4d9930-87ab-4aef-9bce-786762687884",
    'new_name': "Confirm new email address",
    'new_subject': "Confirm new email address",
    'new_content': """Hi ((name)),

Click this link to confirm your new email address:


((url))


If you didn’t try to change the email address for your Notify account, let us know here:


((feedback_url))
""",
    'old_name': "Confirm new email address",
    'old_subject': "Confirm new email address",
    'old_content': """Hi ((name)),

Click this link to confirm your new email address:


((url))


If you didn’t try to change the email address for your GOV.​UK Notify account, let us know here:


((feedback_url))
"""
}, {
    'id': "ece42649-22a8-4d06-b87f-d52d5d3f0a27",
    'new_name': "Notify email verification code",
    'new_subject': "Confirm Notify.gov.au registration",
    'new_content': """Hi ((name)),

To complete your registration for Notify.gov.au please click the link below

((url))
""",
    'old_name': "Notify email verification code",
    'old_subject': "Confirm GOV.AU Notify registration",
    'old_content': """Hi ((name)),

To complete your registration for GOV.AU Notify please click the link below

((url))
"""
}, {
    'id': "299726d2-dba6-42b8-8209-30e1d66ea164",
    'new_name': "Notify email verify code",
    'new_subject': "Sign in to Notify.gov.au",
    'new_content': """Hi ((name)),

To sign in to Notify.gov.au please open this link:
((url))
""",
    'old_name': "Notify email verify code",
    'old_subject': "Sign in to GOV.AU Notify",
    'old_content': """Hi ((name)),

To sign in to GOV.​UK Notify please open this link:
((url))
"""
}, {
    'id': "4f46df42-f795-4cc4-83bb-65ca312f49cc",
    'new_name': "Notify invitation email",
    'new_subject': "((user_name)) has invited you to collaborate on ((service_name)) on Notify.gov.au",
    'new_content': """((user_name)) has invited you to collaborate on ((service_name)) using Notify.


        Notify makes it easy to keep people updated by helping you send text messages and emails.


        Click this link to create a Notify account:
((url))


        This invitation will stop working at midnight tomorrow. This is to keep ((service_name)) secure.
""",
    'old_name': "Notify invitation email",
    'old_subject': "((user_name)) has invited you to collaborate on ((service_name)) on GOV.AU Notify",
    'old_content': """((user_name)) has invited you to collaborate on ((service_name)) on GOV.AU Notify.


        GOV.AU Notify makes it easy to keep people updated by helping you send text messages, emails and letters.


        Click this link to create an account on GOV.AU Notify:
((url))


        This invitation will stop working at midnight tomorrow. This is to keep ((service_name)) secure.
"""
}, {
    'id': "203566f0-d835-47c5-aa06-932439c86573",
    'new_name': "Notify organisation invitation email",
    'new_subject': "((user_name)) has invited you to collaborate on ((organisation_name)) on Notify.gov.au",
    'new_content': """((user_name)) has invited you to collaborate on ((organisation_name)) using Notify.

Notify makes it easy to keep people updated by helping you send text messages and emails. Click this link to create a Notify account:
((url))

This invitation will stop working at midnight tomorrow. This is to keep ((organisation_name)) secure.
""",
    'old_name': "Notify organisation invitation email",
    'old_subject': "((user_name)) has invited you to collaborate on ((organisation_name)) on GOV.AU Notify",
    'old_content': """((user_name)) has invited you to collaborate on ((organisation_name)) on GOV.AU Notify.

GOV.AU Notify makes it easy to keep people updated by helping you send text messages, emails and letters.

Open this link to create an account on GOV.AU Notify:
((url))

This invitation will stop working at midnight tomorrow. This is to keep ((organisation_name)) secure.
"""
}, {
    'id': "474e9242-823b-4f99-813d-ed392e7f1201",
    'new_name': "Notify password reset email",
    'new_subject': "Reset your Notify.gov.au password",
    'new_content': """Hi ((user_name)),

We received a request to reset your password on Notify.

If you didn’t request this email, you can ignore it – your password has not been changed.

To reset your password, click this link:

((url))
""",
    'old_name': "Notify password reset email",
    'old_subject': "Reset your GOV.AU Notify password",
    'old_content': """Hi ((user_name)),

We received a request to reset your password on GOV.AU Notify.

If you didn''t request this email, you can ignore it – your password has not been changed.

To reset your password, click this link:

((url))
"""
}, {
    'id': "36fb0730-6259-4da1-8a80-c8de22ad4246",
    'new_name': "Notify SMS verify code",
    'new_subject': "",
    'new_content': """((verify_code)) is your Notify.gov.au authentication code
""",
    'old_name': "Notify SMS verify code",
    'old_subject': "",
    'old_content': """((verify_code)) is your Notify authentication code
"""
}, {
    'id': "0880fbb1-a0c6-46f0-9a8e-36c986381ceb",
    'new_name': "Your Notify.gov.au account",
    'new_subject': "Your Notify.gov.au account",
    'new_content': """You already have a Notify account with this email address.

Sign in here: ((signin_url))

If you’ve forgotten your password, you can reset it here: ((forgot_password_url))


If you didn’t try to register for a Notify account recently, please let us know here: ((feedback_url))
""",
    'old_name': "Your GOV.UK Notify account",
    'old_subject': "Your GOV.AU Notify account",
    'old_content': """You already have a GOV.AU Notify account with this email address.

Sign in here: ((signin_url))

If you’ve forgotten your password, you can reset it here: ((forgot_password_url))


If you didn’t try to register for a GOV.AU Notify account recently, please let us know here: ((feedback_url))
"""
}]

template_update = """
    UPDATE templates
    SET name = '{}', subject = '{}', content = '{}'
    WHERE id = '{}'
"""
template_history_updae = """
    UPDATE templates_history
    SET name = '{}', subject = '{}', content = '{}'
    WHERE id = '{}'
"""

def upgrade():
    for t in templates:
        op.execute(template_update.format(t['new_name'], t['new_subject'], t['new_content'], t['id']))
        op.execute(template_history_updae.format(t['new_name'], t['new_subject'], t['new_content'], t['id']))


def downgrade():
    for t in templates:
        op.execute(template_update.format(t['old_name'], t['old_subject'], t['old_content'], t['id']))
        op.execute(template_history_updae.format(t['old_name'], t['old_subject'], t['old_content'], t['id']))
