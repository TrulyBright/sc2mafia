import views


def setup_routes(app):
    app.add_route(views.index, "/")
    app.add_route(views.callback, '/oauth')
    app.add_route(views.login, "/login", methods=["GET"])
    app.add_route(views.register_get, "/register", methods=["GET"])
    app.add_route(views.register_post, "/register", methods=["POST"])
    app.add_route(views.main, "/game")
    app.add_route(views.archive, "/archive/<gamelog_id>")
    app.add_route(views.archive_index, "/archive")
    app.add_route(views.about, "/about")
