Return email and text message templates:

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates
```

Return email templates only:

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates?type=email
```

Return text message templates only:

```sh
curl \
    -H "Authorization: Bearer ${JWT}" \
    -H "Content-type: application/json" \
    https://rest-api.notify.gov.au/v2/templates?type=sms
```
