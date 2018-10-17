Return email and text message templates:

```java
TemplateList allTemplates = client.getAllTemplates(null);
```

Return email templates only:

```java
TemplateList emailTemplates = client.getAllTemplates("email");
```

Return text message templates only:

```java
TemplateList smsTemplates = client.getAllTemplates("sms");
```
