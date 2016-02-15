# Logging

`pass`


# Placeholders

Given a message template, the `Placeholders` class can:
- highlight the placeholders (by adding HTML)
- replace the placeholders with data
- extract the names of the placeholders

## If you only have the template

```python
  placeholders = Placeholders("Hello ((name))")
```

### Highlight the placeholders:
```python
  placeholders.formatted
  >>> "Hello <span class='placeholder'>name</span>"
  placeholders.formatted_as_markup
  >>> Markup(u"Hello <span class='placeholder'>name</span>")
```

### List the placeholders in the template
```python
  placeholders.list
  >>> ['name']
  placeholders.marked_up_list
  [Markup(u"<span class='placeholder'>name</span>")]
```


## If you have the template and the user’s data

You can do all of the above, plus

### Replace the placeholders with the user’s data
```python
  placeholders = Placeholders("Hello ((name))", {"name": "Chris"})
  placeholders.replaced
  >>> 'Hello Chris'
```

### Find out what data is missing for a given template
```python
  placeholders = Placeholders("Hello ((name))", {"foo": "bar"})
  placeholders.missing_data
  >>> {'name'}
```

### Find out what additional data is being passed that the template isn’t expecting
```python
  placeholders = Placeholders("Hello ((name))", {"foo": "bar"})
  placeholders.additional_data
  >>> {'foo'}
```

### If you try to replace placeholders with bad data

…then you’ll get a `PlaceholderError`, eg
```python
  placeholders = Placeholders("Hello ((name))", {"foo": "bar"})
  >>> PlaceholderError: Needed by template: name
```
