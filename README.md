# fastapi-flask-auth

Lightweight FastAPI dependencies and authenticator that uses Flask session cookies for access control.

Why would you want to base your FastAPI application's authentication on session cookies created by a Flask application?

Well, imagine that you have a Flask application that handles authentication (probably with `flask-login`) among other tasks and you'd like to use FastAPI for some new routes, or maybe you just want to offload some work from Flask to FastAPI for convenience or performance reasons. In such a scenario, you probably don't want the client to authenticate at both server applications. What you can do instead is put both server applications behind a reverse proxy, let Flask handle authentication and do its job as before, and use Flask's session cookies for authentication in your FastAPI application with this library.

## Installation & Usage

You can install the library from PyPI with `pip install fastapi-flask-auth`.

You will also need to install a Flask session decoder. If you're looking for a lightweight, zero-dependency decoder, give `flask-session-decoder` a try. You can do this manually with `pip install flask-session-decoder` or you can install `fastapi-flask-auth` together with its default decoder dependency simply with `pip install fastapi-flask-auth[decoder]`.

With both `fastapi-flask-auth` and `flask-session-decoder` in place, you can set up the authenticator for your FastAPI application like this:

```python
from fastapi_flask_auth import FlaskSessionAuthenticator
from flask_session_decoder import FlaskSessionDecoder

decoder = FlaskSessionDecoder(secret_key="the-secret-key-of-the-flask-app-that-created-the-cookie")
flask_auth = FlaskSessionAuthenticator(decoder=decoder)
```

Then, you can use the authenticator's FastAPI dependencies in your routes like this:

```python
from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/get-session-cookie")
def get_session_cookie(cookie: dict | None = Depends(flask_auth.get_session_cookie)):
    ...

@app.get("/requires-session-cookie")
def requires_session_cookie(cookie: dict = Depends(flask_auth.requires_session_cookie)):
    ...

@app.get("/get-user-id")
def get_user_id(user_id: str | None = Depends(flask_auth.get_user_id)):
    ...

@app.get("/requires-session-cookie")
def requires_user_id(user_id: str = Depends(flask_auth.requires_user_id)):
    ...
```

## Dependencies

The only dependency of this library is `FastAPI`.

The default decoder dependency is `flask-session-decoder`, which has no further dependencies.

## Development

Use `black` for code formatting and `mypy` for static code analysis.

## License - MIT

The library is open-sourced under the conditions of the MIT [license](https://choosealicense.com/licenses/mit/).
