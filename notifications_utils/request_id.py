import uuid

from flask import request
from flask.wrappers import Request


class CustomRequest(Request):
    _request_id = None

    @property
    def request_id(self):
        if self._request_id is None:
            self._request_id = self._get_request_id(
                'NotifyRequestID',
                'NotifyDownstreamRequestID')
        return self._request_id

    def _get_request_id(self, request_id_header, downstream_header):
        if request_id_header in self.headers:
            return self.headers.get(request_id_header)
        elif downstream_header and downstream_header in self.headers:
            return self.headers.get(downstream_header)
        else:
            return str(uuid.uuid4())


class ResponseHeaderMiddleware(object):
    def __init__(self, app, request_id_header):
        self.app = app
        self.request_id_header = request_id_header

    def __call__(self, environ, start_response):
        def rewrite_response_headers(status, headers, exc_info=None):
            if self.request_id_header not in dict(headers).keys():
                headers = headers + [(
                    self.request_id_header,
                    request.request_id.encode('utf-8')
                )]

            return start_response(status, headers, exc_info)

        return self.app(environ, rewrite_response_headers)


def init_app(app):
    app.request_class = CustomRequest
    app.wsgi_app = ResponseHeaderMiddleware(app.wsgi_app, 'NotifyRequestID')
