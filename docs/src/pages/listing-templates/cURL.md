Return email and sms templates

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates
```

Return email templates only

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates?type=email
```

Return sms templates only

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates?type=sms
```
