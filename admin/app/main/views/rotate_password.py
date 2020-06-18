from flask import render_template, session, url_for, redirect

from app import user_api_client
from app.main import main
from app.main.forms import RotatePasswordForm
from app.utils import redirect_to_sign_in
from app.main.views.two_factor import log_in_user


@main.route('/change-password', methods=['GET', 'POST'])
@redirect_to_sign_in
def rotate_password():
    def _check_if_new_password_is_same_as_current_password(new_password):
        return user_api_client.verify_password(session['user_details']['id'], new_password)

    form = RotatePasswordForm(_check_if_new_password_is_same_as_current_password)

    if form.validate_on_submit():
        session['user_details']['password'] = form.new_password.data
        return log_in_user(session['user_details']['id'])

    return render_template(
        'views/rotate-password.html',
        title='Update your password',
        form=form,
    )
