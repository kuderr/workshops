from flask import request, jsonify
from flask import Flask
from models import db, User, Post, Comment
from functools import wraps


def create_app():
    app = Flask(__name__)

    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_basics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app


app = create_app()


def auth_required(f):
    """
        Декоратор для примера.
        Обязательно переписать под своё приложение.
    """
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Пользователь не красавчик',
            'autheticated': False
        }

        if len(auth_headers) == 2:
            token = auth_headers[1]
            if token == 'Красавчик':
                return f(*args, **kwargs)

        return jsonify(invalid_msg), 401

    return _verify


@app.route('/posts/', methods=['GET'])
@auth_required
def get_posts():
    posts = [post.to_dict() for post in Post.query.all()]
    return jsonify(posts), 200


@app.route('/posts/', methods=['POST'])
@auth_required
def add_post():
    post_data = request.get_json()

    new_post = Post(title=post_data['title'])

    new_post.body = post_data.get('body')
    new_post.author = post_data.get('author')
    new_post.comments = []

    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201


@app.route('/posts/<int:post_id>', methods=['PUT'])
@auth_required
def edit_post(post_id):
    post_data = request.get_json()
    post_to_edit = Post.query.get(post_id)

    post_to_edit.title = post_data['title']
    post_to_edit.body = post_data.get('body')
    post_to_edit.author = post_data.get('author')

    return jsonify({"message": f"Successfully updated post: '{post_to_edit.title}' "}), 200


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@auth_required
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)

    db.session.delete(post_to_delete)
    db.session.commit()

    return jsonify({"message": f"Successfully deleted post: '{post_to_delete.title}' "}), 200


if __name__ == '__main__':
    app.run()
