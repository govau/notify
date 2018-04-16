from urllib.parse import urljoin

import requests
from flask import current_app


class DeskproError(Exception):
    pass


class DeskproClient():
    def __init__(self):
        self.api_key = None
        self.api_host = None

        self.department_id = None
        self.agent_team_id = None
        self.default_person_email = None

    def init_app(self, app, *args, **kwargs):
        self.api_key = app.config.get('DESKPRO_API_KEY')
        self.api_host = app.config.get('DESKPRO_API_HOST')

        self.department_id = app.config.get('DESKPRO_DEPT_ID')
        self.agent_team_id = app.config.get('DESKPRO_ASSIGNED_AGENT_TEAM_ID')
        self.default_person_email = app.config.get('DESKPRO_PERSON_EMAIL')

    def create_ticket(self, subject, message, ticket_type=None, urgency=1,
                      user_name=None, user_email=None):

        data = {
            'subject': subject,
            'message': message,
            'label': ticket_type,
            'department_id': self.department_id,
            'agent_team_id': self.agent_team_id,
            'person_email': user_email or self.default_person_email,
            'person_name': user_name,
            'urgency': urgency,
        }

        headers = {
            "X-DeskPRO-API-Key": self.api_key,
            'Content-Type': "application/x-www-form-urlencoded"
        }

        response = requests.post(
            urljoin(self.api_host, '/api/tickets'),
            data=data,
            headers=headers
        )

        if response.status_code != 201:
            current_app.logger.error(
                "Deskpro create ticket request failed with {} '{}'".format(
                    response.status_code,
                    response.json()
                )
            )

            raise DeskproError()

        return True
