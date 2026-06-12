import os
from flask import request
from flask_babel import Babel

def get_locale():
    """
    Detects the best language match for the current user.
    Checks URL parameters first, then falls back to browser headers.
    """
    # Define the languages your application supports.
    # Example: English, Spanish, Hindi, French, and Mandarin.
    supported_languages = ['en', 'es', 'hi', 'te', 'fr', 'zh']
    
    # 1. Priority: URL parameter (e.g., /api/translate?lang=es)
    lang = request.args.get('lang')
    if lang in supported_languages:
        return lang
    
    # 2. Fallback: Browser 'Accept-Language' header
    return request.accept_languages.best_match(supported_languages)

def init_localization(app):
    """
    Configures Babel for the Flask app.
    Requires strings to be wrapped in gettext calls: _("Hello World")
    """
    babel = Babel(app, locale_selector=get_locale)
    
    # Ensure the translations directory exists for .po/.mo files
    if not os.path.exists('translations'):
        os.makedirs('translations')
    
    return babel