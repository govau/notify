# Logging

`pass`

# Recipients

## Validate a recipient

`validate_phone_number(recipient)` and `validate_email_address(recipient)` will
raise `InvalidPhoneError` and `InvalidEmailError` respectively.

`validate_recipient(recipient, template_type)` accepts a phone number or email
address, and will do the right validation based on the given template type
(`email` or `sms`)

## Handling a CSV file of recipients

Given the content of a CSV file, the `RecipientCSV` class can:
- iterate through the rows
- return the column headers, and show how they relate to a template’s
  placeholders
- find any errors
- reformat the CSV data in a way that’s suitable for front end rendering

It makes extensive use of generators in order to only read as much data into
memory as is needed.

### Get the rows from a CSV file

```python
list(RecipientCSV("phone number\n07700900460").rows)
>>> {'phone number': '07700900460'}
```

### Annotate each field with some useful metadata

- `data` contains the original data for the column
- `error` contains any errors with the data
- `ignored` will be true if the column isn’t in the template’s placeholders
- `index` (added to the row) is a 0-indexed count of the lines in the CSV

```python
list(RecipientCSV("phone number,name\n07700900460,Jo", template_type='sms').annotated_rows)
>>> {
>>>   'index': 0,
>>>   'phone number': {
>>>     'data': '07700900460',
>>>     'error': 'Must be a valid UK mobile number',
>>>     'ignored': False
>>>   },
>>>   'name': {
>>>     'data': 'Jo',
>>>     'error': None,
>>>     'ignored': True
>>>   }
>>> }
```

`.initial_annotated_rows` will do the same thing, but limited to the number of
rows specified when passing `max_initial_rows_shown` to the constructor.

`.annotated_rows_with_errors` will do the same thing, but only return rows that
have errors.

`.initial_annotated_rows_with_errors` will show only errors, up to a limit of
`max_errors_shown` (as passed to the constructor).

### Get just the recipients, just the personalisation, or both

```python
recipients =
list(RecipientCSV(
  "phone number,name\n07700900460,Jo",
  template_type='sms'
).recipients)
>>> ['07700900460']
list(RecipientCSV(
  "phone number,name\n07700900460,Jo",
  template_type='sms',
  placeholders=['name']
).personalisation
>>> [{'name': 'Jo'}]
list(RecipientCSV(
  "phone number,name\n07700900460,Jo",
  template_type='sms',
  placeholders=['name']
).recipients_and_personalisation)
>>> [(['07700900460'], {'name': 'Jo'})]
```
N.B. these methods will only return personalisation for columns that match the
template’s placeholders.

### Get the column headers

```python
RecipientCSV("phone number\n07700900460").column_headers
>>> ['phone number']
```

Also available is `.column_headers_with_placeholders_highlighted`.

### Find errors in the CSV

```python
recipients = RecipientCSV(
  "phone number,registration\n07700900460",
  template_type='sms',
  placeholders=['name']
)
recipients.missing_column_headers
>>> ['name']
list(recipients.rows_with_bad_recipients)
>>> {1}
list(recipients.rows_with_missing_data)
>>> {0}
list(recipients.rows_with_errors)
>>> {1}
recipients.has_errors
>>> True
```

### Add a whitelist of recipients

Will give back errors for any recipients not in the whitelist

```python
recipients = RecipientCSV(
  "phone number\n07700900460",
  template_type='sms',
  whitelist=['07700900999']
)
list(recipients.rows_with_errors)
>>> {1}
```

# Template

Given a template object, the `Template` class can:
- highlight the placeholders (by adding HTML)
- replace the placeholders with data
- extract the names of the placeholders

It will also pass through, if passed the `name` and `id` of the template, and
the user’s data, eg:
```python
  template = Template(
    {"id": "1234", "name": "Hello world", "content": "Hello ((name))"},
    {"name": "chris"}
  )
  template.id
  >>> "1234"
  template.name
  >>> "Hello world"
  template.content
  >>> "Hello ((name))"
  template.values
  >>> {"name": "chris"}
```

## If you only have the template

```python
  template = Template({"content": "Hello ((name))"})
```

### Highlight the placeholders:
```python
  template.formatted
  >>> "Hello <span class='placeholder'>name</span>"
  template.formatted_as_markup
  >>> Markup(u"Hello <span class='placeholder'>name</span>")
```

### List the placeholders in the template
```python
  template.placeholders
  >>> ['name']
  template.placeholders_as_markup
  >>> [Markup(u"<span class='placeholder'>name</span>")]
```

### Prefix the message with the service name
```python
  template = Template({"content": "Hello world"}, prefix="My service")
  template.formatted
  >>> Markup(u"My service: Hello world")
  template.content
  >>> "Hello world"
```

## If you have the template and the user’s data

You can do all of the above, plus

### Replace the placeholders with the user’s data
```python
  template = Template({"content": "Hello ((name))"}, {"name": "Chris"})
  template.replaced
  >>> 'Hello Chris'
```

### Find out what data is missing for a given template
```python
  template = Template({"content": "Hello ((name))}", {"foo": "bar"})
  template.missing_data
  >>> {'name'}
```

### Find out what additional data is being passed that the template isn’t expecting

…or ignore some additional data

```python
  template = Template({"content": "Hello ((name))"}, {"foo": "bar"})
  template.additional_data
  >>> {'foo'}
  template = Template({"content": "Hello ((name))"}, {"foo": "bar"}, drop_values=('foo'))
  template.additional_data
  >>> {}
```

### If you try to replace placeholders with bad data

…then you’ll get a `NeededByTemplateError` or a `NoPlaceholderForDataError`, eg
```python
  template = Template({"content": "Hello ((name))"}, {"foo": "bar"})
  >>> NeededByTemplateError: name
```
