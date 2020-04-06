from app.models import Rate


def list_rates():
    return Rate.query.all()
