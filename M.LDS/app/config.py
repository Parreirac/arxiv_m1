"""Fichier de configuration pour l'application"""
class Config():
    """Base parameters"""
    name = "Module_0"
    version = "1.0.0"
    url = "https://github.com/Parreirac/arxiv_m1/tree/master/M.LDS"
    license = "MIT (see https://opensource.org/licenses/MIT)"
    UPLOAD_FOLDER: str = './uploads/'
    ALLOWED_EXTENSIONS = {'tex', 'pdf'}
    MAX_CONTENT_LENGTH: int = 40 * 1000 * 1000
    # TODO TEST If a larger file Flask will raise a RequestEntityTooLarge
    secret_key: str = "not super secret key"

class ProdConfig(Config):
    """Prod parameters"""
    DEBUG = False

class DevConfig(Config):
    """Developers parameters"""
    SESSION_LIFETIME = 1 # TODO PRA ?
    DEBUG = True
