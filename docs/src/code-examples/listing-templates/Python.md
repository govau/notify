Return email and text message templates:

```python
response = notifications_client.get_all_templates()
```

Return email templates only:

```python
response = notifications_client.get_all_templates(template_type="email")
```

Return text message templates only:

```python
response = notifications_client.get_all_templates(template_type="sms")
```