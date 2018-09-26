from flask import Response
from urllib import parse

from app.main import main
from app.main.s3_client import clients as s3_clients


@main.route("/static-logo/<path:logo>")
def static_logo(logo):
    # TODO: delete this and use a real cdn instead of this

    s3_object = s3_clients.logo.get_object(parse.unquote_plus(logo))
    response = s3_object.get()

    return Response(
        response['Body'].iter_chunks(),
        headers=response['ResponseMetadata']['HTTPHeaders']
    )
