



UPLOAD_FOLDER: str = '/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH: int = 40 * 1000 * 1000      # TODO TEST If a larger file is transmitted, Flask will raise a RequestEntityTooLarge exception.

class Config(object):
    pass

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
