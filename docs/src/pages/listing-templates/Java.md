Return email and sms templates

```java
TemplateList allTemplates = client.getAllTemplates(null);
```

Return email templates only

```java
TemplateList emailTemplates = client.getAllTemplates("email");
```

Return sms templates only

```java
TemplateList smsTemplates = client.getAllTemplates("sms");
```
