import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        query = 'SELECT * FROM user WHERE id = ?'
        g.user = get_db().execute(query, (user_id,)).fetchone()


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Введите имя пользователя'
        elif not password:
            error = 'Введите пароль'

        if error is None:
            try:
                stmt = "INSERT INTO user (username, password) VALUES (?, ?)"
                db.execute(stmt, (username, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                error = f"Пользователь {username} уже существует"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        query = 'SELECT * FROM user WHERE username = ?'
        user = db.execute(query, (username,)).fetchone()

        if user is None:
            error = 'Проверьте имя пользователя'
        elif not check_password_hash(user['password'], password):
            error = 'Проверьте пароль'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
