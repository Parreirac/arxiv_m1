# https://github.com/flask-extensions/Flask-SimpleLogin/blob/main/example/simple_app.py
from flask import Flask, jsonify, render_template
from flask.views import MethodView
from flask_simplelogin import SimpleLogin, get_username, login_required

my_users = {
    "chuck": {"password": "norris", "roles": ["admin"]},
    "lee": {"password": "douglas", "roles": []},
    "mary": {"password": "jane", "roles": []},
    "steven": {"password": "wilson", "roles": ["admin"]},
}


def check_my_users(user):
    """Check if user exists and its credentials.
    Take a look at encrypt_app.py and encrypt_cli.py
     to see how to encrypt passwords
    """
    user_data = my_users.get(user["username"])
    if not user_data:
        return False  # <--- invalid credentials
    elif user_data.get("password") == user["password"]:
        return True  # <--- user is logged in!

    return False  # <--- invalid credentials


app = Flask(__name__)
app.config.from_object("settings")
app.secret_key = "secret-here"

simple_login = SimpleLogin(app, login_checker=check_my_users)


@app.route("/")
def index():


    return "{% "+render_template('base.html')+"%}\n"+"""{% block title %}Index{% endblock %}

{% block page_body %}
    <div class="row">
        <p>
            Content comes here!
        </p>
    </div>
{% endblock %}"""


@app.route("/secret")
@login_required(username=["chuck", "mary"])
def secret():
    return """{% extends 'base.html' %}
{% block title %}Secret{% endblock %}

{% block page_body %}
    <div class="row">
        <p>
            <h1>This is secret!! You can see only because you are {{ get_username() }}</h1>
        </p>
    </div>
{% endblock %}
    """


@app.route("/api", methods=["POST"])
@login_required(basic=True)
def api():
    return jsonify(data="You are logged in with basic auth")


def be_admin(username):
    """Validator to check if user has admin role"""
    user_data = my_users.get(username)
    if not user_data or "admin" not in user_data.get("roles", []):
        return "User does not have admin role"


def have_approval(username):
    """Validator: all users approved, return None"""
    return


@app.route("/complex")
@login_required(must=[be_admin, have_approval])
def complexview():
    return """{% extends 'base.html' %}
{% block title %}Secret{% endblock %}

{% block page_body %}
    <div class="row">
        <p>
            <h1>This is secret!! You can see only because you are {{ get_username() }}</h1>
        </p>
    </div>
{% endblock %}"""


class ProtectedView(MethodView):
    decorators = [login_required]

    def get(self):
        return "You are logged in as <b>{0}</b>".format(get_username())


app.add_url_rule("/protected", view_func=ProtectedView.as_view("protected"))

if __name__ == "__main__":
    app.run(debug=True) # host="0.0.0.0", port=5000, use_reloader=True, debug=True)
