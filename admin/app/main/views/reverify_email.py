import json
from flask import request, render_template, session, abort, current_app, flash, redirect, url_for
from flask_login import current_user
from notifications_utils.url_safe_token import check_token
from itsdangerous import SignatureExpired
from app import user_api_client
from app.main import main
from app.utils import redirect_to_sign_in
from app.main.views.two_factor import log_in_user


# when a user follows a reverify email link
@main.route('/reverify-email-token/<token>')
def reverify_email_token(token):
    try:
        token_data = check_token(
            token,
            current_app.config['SECRET_KEY'],
            current_app.config['DANGEROUS_SALT'],
            current_app.config['EMAIL_EXPIRY_SECONDS']
        )
    except SignatureExpired:
        flash('The link in the email we sent you has expired. We\'ve sent you a new one.')
        return redirect(url_for('main.resend_email_reverification'))

    token_data = json.loads(token_data)
    user = user_api_client.get_user(token_data['user_id'])

    if not user:
        abort(404)

    session['user_details'] = {
        'email': user.email_address,
        'id': user.id,
        'set_last_verified_at': True,
    }

    return log_in_user(user.id)


# reverify page
@main.route('/reverify-email', methods=['GET'])
@redirect_to_sign_in
def reverify_email():
    title = 'Email resent' if request.args.get('email_resent') else 'Check your inbox'

    return render_template(
        'views/reverify-email.html',
        title=title
    )


# reverify email not received page
@main.route('/reverify-email-not-received', methods=['GET'])
@redirect_to_sign_in
def reverify_email_not_received():
    return render_template(
        'views/email-not-received.html',
        url=url_for('main.resend_email_reverification'),
    )


# send the reverify email
@main.route('/send-new-email-reverification', methods=['GET'])
@redirect_to_sign_in
def resend_email_reverification():
    user_api_client.send_reverify_email(session['user_details']['id'], session['user_details']['email'])
    return redirect(url_for('main.reverify_email', email_resent=True))
