"""
The Flask app, shared by the local dev server and the Vercel function.

Routes
  GET  /                 continue watching and my list
  GET  /search           ?q=&lang=
  GET  /watch/<id>       ?t=&c=&y=&l=   player
  GET  /watchlist
  GET  /settings         POST saves the default language
  GET  /convert          ?u=  and optionally &check=1
  GET  /title/<kind>/<id>  ?s=&e=  one film or one episode, and its player
"""

import os

from urllib.parse import quote, urlsplit

from flask import Flask, Response, jsonify, redirect, request

from . import einthusan as E
from . import accounts
from . import views

# v2 on purpose: visitors who loaded the old default (tamil) once were given
# a cookie for it, and it would otherwise outlive the change to English.
TOP_LANG_COOKIE = "einthuflix_lang"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365
SESSION_COOKIE = "einthuflix_session"


def _valid_lang(value):
    """Every language here is an einthusan catalogue."""
    code = (value or "").strip().lower()
    return code if code in E.LANG_CODES else "tamil"


def create_app():
    # this module lives in lib/, so Flask would otherwise look for lib/static
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        static_folder=os.path.join(project_root, "static"),
        static_url_path="/static",
    )
    app.config["JSON_SORT_KEYS"] = False

    def top_lang():
        return _valid_lang(request.cookies.get(TOP_LANG_COOKIE, "tamil"))

    def render(name, body, lang=None):
        lang = lang or top_lang()
        html = views.page(name, body, lang)
        resp = Response(html, mimetype="text/html; charset=utf-8")
        if not request.cookies.get(TOP_LANG_COOKIE):
            resp.set_cookie(TOP_LANG_COOKIE, lang,
                            max_age=COOKIE_MAX_AGE, samesite="Lax")
        return resp

    def current_user():
        return accounts.user_for_token(request.cookies.get(SESSION_COOKIE))

    def auth_response(payload, status=200):
        if not request.is_json:
            return redirect("/settings", code=303)
        return jsonify(payload), status

    def require_user():
        user = current_user()
        if not user:
            return None, (jsonify({"error": "Login required."}), 401)
        return user, None

    # ---------------------------------------------------------------- home
    @app.route("/")
    def home():
        _name, body, _l = views.home_page(top_lang())
        return render("Home", body)

    # -------------------------------------------------------------- search
    @app.route("/search")
    def search():
        query = (request.args.get("q") or "").strip()[:80]
        lang = _valid_lang(request.args.get("lang") or top_lang())

        if not query:
            _n, body, _l = views.search_page("", lang, [], 0, 0, None, lang)
            return render("Search", body, lang)

        # a watch url pasted into the search box means "convert"
        if E._WATCH.search(query) or E._CONTENT.search(query):
            return convert()

        try:
            got = E.search(query, lang)
        except Exception:
            got = None

        if got is None:
            items, pages, count, used = [], 0, 0, query
            failed = True
        else:
            items, pages, count, used = got
            failed = False

        # No model call on the search path. A dead end has to answer as fast
        # as a hit, so suggestions are not worth the extra round trip here.
        _n, body, _l = views.search_page(query, lang, items, pages, count,
                                         used, lang)
        if failed:
            body = ('<p class="empty bad">Could not reach einthusan just now. '
                    'Wait a moment and try again.</p>' + body)
        return render("Search", body, lang)

    # -------------------------------------------------------------- player
    @app.route("/watch/<movie_id>")
    def watch(movie_id):
        movie_id = E.extract_id(movie_id) or movie_id
        # einthusan signs the media url per page view and it dies six hours
        # later, so it is fetched here, for this page, and not stored anywhere.
        media = E.stream(movie_id) or {}
        item = {
            "id": movie_id,
            "title": (request.args.get("t") or media.get("title")
                      or movie_id)[:120],
            "cover": request.args.get("c") or None,
            "year": request.args.get("y") or "",
            "lang": request.args.get("l") or "",
            "url": media.get("url") or "",
        }
        _n, body, _l = views.watch_page(item, top_lang())
        return render(item["title"], body)

    # ----------------------------------------------------------- watchlist
    @app.route("/watchlist")
    def watchlist():
        _n, body, _l = views.watchlist_page(top_lang())
        return render("Watchlist", body)

    # ------------------------------------------------------------ settings
    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            lang = _valid_lang((request.form.get("toplang") or "tamil").lower())
            resp = redirect("/settings", code=303)
            resp.set_cookie(TOP_LANG_COOKIE, lang,
                            max_age=COOKIE_MAX_AGE, samesite="Lax")
            return resp
        _n, body, _l = views.settings_page(top_lang())
        return render("Settings", body)

    # --------------------------------------------------------------- account
    @app.route("/auth/me")
    def auth_me():
        user = current_user()
        return jsonify({"authenticated": bool(user), "user": user})

    @app.route("/auth/register", methods=["POST"])
    def auth_register():
        data = request.get_json(silent=True) or request.form
        try:
            user, error, status = accounts.register(
                data.get("username", ""), data.get("password", ""),
                request.remote_addr or "")
        except accounts.Unavailable:
            return auth_response({"error": "Account storage is unavailable."}, 503)
        if not user:
            return auth_response({"error": error}, status)
        token = accounts.create_session(user["username"])
        response = auth_response({"authenticated": True, "user": user}, 201)
        if request.is_json:
            response[0].set_cookie(SESSION_COOKIE, token, max_age=accounts.SESSION_DAYS * 86400,
                                   httponly=True, samesite="Lax")
        else:
            response = redirect("/settings", code=303)
            response.set_cookie(SESSION_COOKIE, token, max_age=accounts.SESSION_DAYS * 86400,
                                httponly=True, samesite="Lax")
        return response

    @app.route("/auth/login", methods=["POST"])
    def auth_login():
        data = request.get_json(silent=True) or request.form
        try:
            user, error, status = accounts.login(
                data.get("username", ""), data.get("password", ""),
                request.remote_addr or "")
        except accounts.Unavailable:
            return auth_response({"error": "Account storage is unavailable."}, 503)
        if not user:
            return auth_response({"error": error}, status)
        token = accounts.create_session(user["username"])
        response = auth_response({"authenticated": True, "user": user})
        if request.is_json:
            response[0].set_cookie(SESSION_COOKIE, token, max_age=accounts.SESSION_DAYS * 86400,
                                   httponly=True, samesite="Lax")
        else:
            response = redirect("/settings", code=303)
            response.set_cookie(SESSION_COOKIE, token, max_age=accounts.SESSION_DAYS * 86400,
                                httponly=True, samesite="Lax")
        return response

    @app.route("/auth/logout", methods=["POST"])
    def auth_logout():
        token = request.cookies.get(SESSION_COOKIE)
        accounts.delete_session(token)
        response = auth_response({"authenticated": False})
        response[0].delete_cookie(SESSION_COOKIE) if request.is_json else response.delete_cookie(SESSION_COOKIE)
        return response

    @app.route("/api/sync", methods=["GET", "POST"])
    def sync_state():
        user, error = require_user()
        if error:
            return error
        if request.method == "GET":
            state, rev, updated = accounts.load_state(user["username"])
            return jsonify({"state": state, "rev": rev, "updated": updated})
        incoming = request.get_json(silent=True)
        if not isinstance(incoming, dict):
            return jsonify({"error": "A JSON state object is required."}), 400
        try:
            state, rev, updated = accounts.save_state(user["username"], incoming)
        except ValueError:
            return jsonify({"error": "Sync data is too large."}), 413
        except accounts.Unavailable:
            return jsonify({"error": "Account storage is unavailable."}), 503
        return jsonify({"state": state, "rev": rev, "updated": updated})

    @app.route("/api/sync/clear", methods=["POST"])
    def sync_clear():
        user, error = require_user()
        if error:
            return error
        state, rev, updated = accounts.clear_state(user["username"])
        return jsonify({"state": state, "rev": rev, "updated": updated})

    # ------------------------------------------------------------- convert
    @app.route("/convert")
    def convert():
        raw = (request.args.get("u") or "").strip()[:500]
        movie_id = E.extract_id(raw)
        if not movie_id:
            _n, body, _l = views.convert_page(
                raw, "", None, "",
                "No movie id found in that. Paste a full einthusan link such as "
                "https://einthusan.tv/movie/watch/7C8l/, or just type the "
                "4-character id (7C8l).")
            return render("Convert", body)

        ok, ctype = None, ""
        if request.args.get("check") == "1":
            try:
                ok, ctype = _verify(movie_id)
            except Exception:
                ok, ctype = False, ""
        _n, body, _l = views.convert_page(raw, movie_id, ok, ctype, "")
        return render("Convert", body)

    # -------------------------------------------------------------- library
    # The library page is gone: English is a language on /search now, and the
    # old addresses keep working for anything already bookmarked.
    @app.route("/library")
    def library():
        return redirect("/search", code=303)

    @app.route("/library/search")
    def library_search():
        query = (request.args.get("q") or "").strip()[:80]
        target = "/search"
        if query:
            target += "&q=" + quote(query)
        return redirect(target, code=303)

    # ---------------------------------------------------------------- misc
    @app.route("/healthz")
    def healthz():
        # A missing database must report itself, not take the endpoint down.
        try:
            dialect = accounts._store().dialect
        except Exception:
            dialect = "unavailable"
        return {"ok": True, "groq": bool(os.environ.get("GROQ_API_KEY")),
                "database": dialect}

    @app.errorhandler(404)
    def not_found(_e):
        return redirect("/")

    return app


def _verify(movie_id):
    """Range-probe the media url einthusan has just signed for this film.

    The unsigned /etv/content/D<id>.mp4 this used to check now answers 404 for
    every film, so the probe has to follow the player and use the signed url.
    """
    import http.client
    import ssl as ssl_mod

    media = E.stream(movie_id)
    if not media:
        return False, ""
    parts = urlsplit(media["url"])
    conn = http.client.HTTPSConnection(parts.hostname, timeout=20,
                                       context=ssl_mod.create_default_context())
    try:
        conn.request("GET", parts.path + "?" + parts.query,
                     headers={"User-Agent": E.UA, "Range": "bytes=0-255",
                              "Connection": "close"})
        resp = conn.getresponse()
        ctype = resp.getheader("Content-Type", "")
        resp.read(256)
        return resp.status in (200, 206) and "video" in ctype, ctype
    finally:
        conn.close()
