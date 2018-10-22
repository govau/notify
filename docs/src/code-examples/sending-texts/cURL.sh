curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    --request POST \
    --data '{
      "template_id": "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",
      "phone_number": "0423 555 555",
      "personalisation": {
        "user_name": "Lisa",
        "amount_owing": "$15.50"
      }
    }' \
    https://rest-api.notify.gov.au/v2/notifications/sms
