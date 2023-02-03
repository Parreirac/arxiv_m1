"""Fichier de configuration pour l'application"""


class Config:
    """Base parameters"""
    NAME = "Module_0"
    VERSION = "1.0.0"
    URL = "https://github.com/Parreirac/arxiv_m1/tree/master/M.LDS"
    LICENSE = "MIT (see https://opensource.org/licenses/MIT)"
    UPLOAD_FOLDER = './uploads/'
    ALLOWED_EXTENSIONS = {'tex', 'pdf'}
    MAX_CONTENT_LENGTH = 10 * 1000 * 1000
    SECRET_KEY = "not super secret key"


class ProdConfig(Config):
    """Prod parameters"""
    DEBUG = False


class DevConfig(Config):
    """Developers parameters"""
    # SESSION_LIFETIME = 1
    DEBUG = True
