HashMap<String, String> personalisation = new HashMap<>();
personalisation.put("user_name", "Lisa");

SendSmsResponse response = client.sendSms(
    "f33517ff-2a88-4f6e-b855-xxxxxxxxxxxx",
    "+61 423 555 555",
    personalisation,
    "your-unique-reference-id");
