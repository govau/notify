const mockGraphQLResponse = {
  allCodeSamples: {
    edges: [
      {
        node: {
          content:
            'import au.gov.notify.NotifyClient;\n\nNotifyClient client = new NotifyClient(apiKey);\n',
          extension: 'java',
          relativePath: 'getting-started/Java.java',
          name: 'Java',
        },
      },
      {
        node: {
          content:
            'from notifications_python_client.notifications import NotificationsAPIClient\n\nnotifications_client = NotificationsAPIClient(api_key)\n',
          extension: 'py',
          relativePath: 'getting-started/Python.py',
          name: 'Python',
        },
      },
      {
        node: {
          content:
            "If you are using Gradle:\n\n```groovy\nrepositories {\n    jcenter()\n}\n...\ncompile 'au.gov.notify:notify-client-java:4.0.0-RELEASE'\n```\n\nIf you are using Maven:\n\n```xml\n<repositories>\n  <repository>\n    <id>central</id>\n    <name>bintray</name>\n    <url>http://jcenter.bintray.com</url>\n  </repository>\n</repositories>\n...\n<dependency>\n  <groupId>au.gov.notify</groupId>\n  <artifactId>notify-client-java</artifactId>\n  <version>4.0.0-RELEASE</version>\n  <type>pom</type>\n</dependency>\n```\n",
          extension: 'md',
          relativePath: 'installation/Java.md',
          name: 'Java',
        },
      },
      {
        node: {
          content:
            'HashMap<String, String> personalisation = new HashMap<String, String>();\npersonalisation.put("user_name", "Lisa");\n\nSendEmailResponse response = client.sendEmail(\n    "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",\n    "lisa@example.com",\n    personalisation,\n    "your-unique-reference-id");\n',
          extension: 'java',
          relativePath: 'sending-emails/Java.java',
          name: 'Java',
        },
      },
      {
        node: {
          content: 'pip install --upgrade govau-platforms-notify\n',
          extension: 'sh',
          relativePath: 'installation/Python.sh',
          name: 'Python',
        },
      },
      {
        node: {
          content:
            'curl \\\n    -H "Authorization: Bearer ${JWT}" \\\n    -H "Content-type: application/json" \\\n    --request POST \\\n    --data \'{\n      "template_id": "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",\n      "email_address": "lisa@example.com",\n      "personalisation": {\n        "user_name": "Lisa",\n        "amount_owing": "$15.50"\n      }\n    }\' \\\n    https://rest-api.notify.gov.au/v2/notifications/email\n',
          extension: 'sh',
          relativePath: 'sending-emails/cURL.sh',
          name: 'cURL',
        },
      },
      {
        node: {
          content:
            "client.send_email_notification(\n    email_address='lisa@example.com',\n    template_id='f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx',\n    personalisation={\n        'user_name': 'Lisa',\n        'amount_owing': '$15.50'\n    }\n)\n",
          extension: 'py',
          relativePath: 'sending-emails/Python.py',
          name: 'Python',
        },
      },
      {
        node: {
          content:
            'HashMap<String, String> personalisation = new HashMap<>();\npersonalisation.put("user_name", "Lisa");\n\nSendSmsResponse response = client.sendSms(\n    "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",\n    "+61 423 555 555",\n    personalisation,\n    "your-unique-reference-id");\n',
          extension: 'java',
          relativePath: 'sending-texts/Java.java',
          name: 'Java',
        },
      },
      {
        node: {
          content:
            "client.send_sms_notification(\n    phone_number='+61423 555 555',\n    template_id='f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx',\n    personalisation={\n        'user_name': 'Lisa',\n        'amount_owing': '$15.50'\n    }\n)\n",
          extension: 'py',
          relativePath: 'sending-texts/Python.py',
          name: 'Python',
        },
      },
      {
        node: {
          content:
            'curl \\\n    -H "Authorization: Bearer ${JWT}" \\\n    -H "Content-type: application/json" \\\n    --request POST \\\n    --data \'{\n      "template_id": "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",\n      "phone_number": "0423 555 555",\n      "personalisation": {\n        "user_name": "Lisa",\n        "amount_owing": "$15.50"\n      }\n    }\' \\\n    https://rest-api.notify.gov.au/v2/notifications/sms\n',
          extension: 'sh',
          relativePath: 'sending-texts/cURL.sh',
          name: 'cURL',
        },
      },
    ],
  },
}

export default mockGraphQLResponse
