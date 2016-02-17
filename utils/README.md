# Logging

`pass`


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
