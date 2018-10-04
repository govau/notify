notifications_client.send_email_notification(
    email_address='lisa@example.com',
    template_id='f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx',
    personalisation={
        'user_name': 'Lisa',
        'amount_owing': '$15.50'
    }
)
