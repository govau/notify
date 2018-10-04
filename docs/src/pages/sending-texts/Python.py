notifications_client.send_sms_notification(
    phone_number='+61423 555 555',
    template_id='f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx',
    personalisation={
        'user_name': 'Lisa',
        'amount_owing': '$15.50'
    }
)
