from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


def get_post(post_id, check_author=True):
    query = '''
        SELECT p.id, title, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        WHERE p.id = ?
    '''
    post = get_db().execute(query, (post_id,)).fetchone()
    if post is None:
        abort(404, f"Пост с id {post_id} не найден")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/')
@login_required
def index():
    db = get_db()
    query = '''
        SELECT p.id, title, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY created DESC
    '''
    posts = db.execute(query).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Введите название поста'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            stmt = '''
                INSERT INTO post (title, body, author_id)
                VALUES (?, ?, ?)
            '''
            db.execute(stmt, (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Введите название поста'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            stmt = '''
                UPDATE post SET title = ?, body = ?
                WHERE id = ?
            '''
            db.execute(stmt, (title, body, post_id))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()
    stmt = 'DELETE FROM post WHERE id = ?'
    db.execute(stmt, (post_id,))
    db.commit()
    return redirect(url_for('blog.index'))
