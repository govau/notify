import flask.json
from datetime import datetime
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from notify.errors import HTTPError

from app import (
    current_service,
    invite_api_client,
    service_api_client,
    user_api_client,
)

from app.utils import gmt_timezones
from app.main import main
from app.main.forms import InviteUserForm, PermissionsForm, SearchUsersForm
from app.notify_client.models import roles, all_permissions
from app.utils import user_has_permissions, Spreadsheet, user_is_platform_admin, json_download


@main.route("/services/<service_id>/users")
@login_required
@user_has_permissions('view_activity')
def manage_users(service_id):
    users = sorted(
        user_api_client.get_users_for_service(service_id=service_id) + [
            invite for invite in invite_api_client.get_invites_for_service(service_id=service_id)
            if invite.status != 'accepted'
        ],
        key=lambda user: user.email_address,
    )

    return render_template(
        'views/manage-users.html',
        users=users,
        current_user=current_user,
        show_search_box=(len(users) > 7),
        form=SearchUsersForm(),
    )


@main.route("/services/<service_id>/users.json")
@login_required
@user_is_platform_admin
def service_users_report_json(service_id):
    # permissions are structured differently on invited vs accepted-invite users
    def user_permissions(user):
        return {
            permission for permission in all_permissions if
            user.has_permission_for_service(service_id, permission)
        }

    def present_row(user):
        logged_in_at = getattr(user, 'logged_in_at', None)
        if logged_in_at:
            logged_in_at = gmt_timezones(logged_in_at)

        return {
            "email_address": user.email_address,
            "name": getattr(user, 'name', None),  # does not exist on invited user
            "mobile_number": getattr(user, 'mobile_number', None),  # does not exist on invited user
            "last_login": logged_in_at,
            "auth_type": user.auth_type,
            "permissions": list(user_permissions(user)),
        }

    users = sorted(
        user_api_client.get_users_for_service(service_id=service_id) + [
            invite for invite in invite_api_client.get_invites_for_service(service_id=service_id)
            if invite.status != 'accepted'
        ],
        key=lambda user: user.email_address,
    )

    return json_download([present_row(user) for user in users], f'service-{service_id}-users')


@main.route("/services/<service_id>/users.csv")
@login_required
@user_has_permissions('manage_service')
def service_users_report(service_id):
    # permissions are structured differently on invited vs accepted-invite users
    def user_permissions(user):
        return {
            permission for permission in all_permissions if
            user.has_permission_for_service(service_id, permission)
        }

    def present_row(user):
        logged_in_at = getattr(user, 'logged_in_at', None)
        if logged_in_at:
            logged_in_at = gmt_timezones(logged_in_at)

        return [
            user.email_address,
            getattr(user, 'name', None),  # does not exist on invited user
            getattr(user, 'mobile_number', None),  # does not exist on invited user
            logged_in_at,
            user.auth_type,
            ';'.join(user_permissions(user))
        ]

    users = sorted(
        user_api_client.get_users_for_service(service_id=service_id) + [
            invite for invite in invite_api_client.get_invites_for_service(service_id=service_id)
            if invite.status != 'accepted'
        ],
        key=lambda user: user.email_address,
    )

    columns = ["email_address", "name", "mobile_number", "last_login", "auth_type", "permissions"]
    csv_data = [columns, *(present_row(user) for user in users)]
    return Spreadsheet.from_rows(csv_data).as_csv_data, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'inline; filename="service-{service_id}-users.csv"'
    }


@main.route("/services/<service_id>/users/invite", methods=['GET', 'POST'])
@login_required
@user_has_permissions('manage_service')
def invite_user(service_id):

    form = InviteUserForm(
        invalid_email_address=current_user.email_address
    )

    service_has_email_auth = 'email_auth' in current_service['permissions']
    if not service_has_email_auth:
        form.login_authentication.data = 'sms_auth'

    if form.validate_on_submit():
        email_address = form.email_address.data
        permissions = get_permissions_from_form(form)
        invited_user = invite_api_client.create_invite(
            current_user.id,
            service_id,
            email_address,
            permissions,
            form.login_authentication.data
        )

        flash('Invite sent to {}'.format(invited_user.email_address), 'default_with_tick')
        return redirect(url_for('.manage_users', service_id=service_id))

    return render_template(
        'views/invite-user.html',
        form=form,
        service_has_email_auth=service_has_email_auth
    )


@main.route("/services/<service_id>/users/<user_id>", methods=['GET', 'POST'])
@login_required
@user_has_permissions('manage_service')
def edit_user_permissions(service_id, user_id):
    service_has_email_auth = 'email_auth' in current_service['permissions']
    # TODO we should probably using the service id here in the get user
    # call as well. eg. /user/<user_id>?&service=service_id
    user = user_api_client.get_user(user_id)
    user_has_no_mobile_number = user.mobile_number is None

    form = PermissionsForm(
        **{role: user.has_permission_for_service(service_id, role) for role in roles.keys()},
        login_authentication=user.auth_type
    )
    if form.validate_on_submit():
        user_api_client.set_user_permissions(
            user_id, service_id,
            permissions=set(get_permissions_from_form(form)),
        )
        if service_has_email_auth:
            user_api_client.update_user_attribute(user_id, auth_type=form.login_authentication.data)
        return redirect(url_for('.manage_users', service_id=service_id))

    return render_template(
        'views/edit-user-permissions.html',
        user=user,
        form=form,
        service_has_email_auth=service_has_email_auth,
        user_has_no_mobile_number=user_has_no_mobile_number
    )


@main.route("/services/<service_id>/users/<user_id>/delete", methods=['GET', 'POST'])
@login_required
@user_has_permissions('manage_service')
def remove_user_from_service(service_id, user_id):
    user = user_api_client.get_user(user_id)
    # Need to make the email address read only, or a disabled field?
    # Do it through the template or the form class?
    form = PermissionsForm(**{
        role: user.has_permission_for_service(service_id, role) for role in roles.keys()
    })

    if request.method == 'POST':
        try:
            service_api_client.remove_user_from_service(service_id, user_id)
        except HTTPError as e:
            msg = "You cannot remove the only user for a service"
            if e.status_code == 400 and msg in e.message:
                flash(msg, 'info')
                return redirect(url_for(
                    '.manage_users',
                    service_id=service_id))
            else:
                abort(500, e)

        return redirect(url_for(
            '.manage_users',
            service_id=service_id
        ))

    flash('Are you sure you want to remove {}?'.format(user.name), 'remove')
    return render_template(
        'views/edit-user-permissions.html',
        user=user,
        form=form
    )


@main.route("/services/<service_id>/cancel-invited-user/<invited_user_id>", methods=['GET'])
@user_has_permissions('manage_service')
def cancel_invited_user(service_id, invited_user_id):
    invite_api_client.cancel_invited_user(service_id=service_id, invited_user_id=invited_user_id)

    return redirect(url_for('main.manage_users', service_id=service_id))


def get_permissions_from_form(form):
    # view_activity is a default role to be added to all users.
    # All users will have at minimum view_activity to allow users to see notifications,
    # templates, team members but no update privileges
    selected_roles = {role for role in roles.keys() if form[role].data is True}
    selected_roles.add('view_activity')
    return selected_roles
