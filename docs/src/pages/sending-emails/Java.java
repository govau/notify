HashMap<String, String> personalisation = new HashMap<String, String>();
personalisation.put("user_name", "Lisa");

SendEmailResponse response = client.sendEmail(
    "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",
    "lisa@example.com",
    personalisation,
    "your-unique-reference-id");