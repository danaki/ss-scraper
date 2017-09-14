from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.profile import Profiler

from flask import (Blueprint, request, session, g, redirect, url_for,
     abort, render_template, flash)

from public import (nav, main, cars, flats)

def create_app(configfile=None):
    app = Flask(__name__)

    AppConfig(app, configfile)
    Bootstrap(app)
    app.debug = True
    Profiler(app)

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(cars, url_prefix='/cars')
    app.register_blueprint(flats, url_prefix='/flats')

    nav.init_app(app)
    # toolbar = DebugToolbarExtension(app)

    return app
