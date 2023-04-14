# import logging
# from logging import config

import logging.config

#STARTDIRECTORY: str = "./../"
#pdfRepository = "./Files/"  # directory must exist... TODO ?
#dataBase = 'myArXive.db'

STARTDIRECTORY: str = "D:/mon_depot/" #"./../"
PDFREPOSITORY = "./Files/"  # directory must exist... TODO ?
DATABASE = 'myArXive.db'

FORMATTER = logging.Formatter("%(asctime)s — %(filename)s — %(funcName)s — %(levelname)s — %(message)s")
LOG_FILE = "my_app.log"

#
'[%(levelname)s:%(asctime)s] %(message)s'

MY_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s:%(module)s] %(filename)s:%(funcName)s:%(lineno)s %(message)s'
        },
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'root': {
            'handlers': ['stream_handler'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# version de base
logging.config.dictConfig(MY_LOGGING_CONFIG)

# # Use FileHandler() to log to a file
# file_handler = logging.FileHandler("mylogs.log")
# log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# formatter = logging.Formatter(log_format)
# file_handler.setFormatter(formatter)
# # Don't forget to add the file handler
# logger.addHandler(file_handler)

""" 
%(asctime)s Date au format « AAAA-MM-JJ HH:MM:SS,xxx ». Remarquons que nous disposons d'une précision à la milliseconde
%(created)f Idem précédent, mais avec une date en timestamp (utilisation de time.time())
%(filename)s Nom du fichier ayant écrit dans le log
%(funcName)s Nom de la fonction contenant l'appel à l'écriture dans le log
%(levelname)s Niveau du message
%(levelno)s Numérotation logique du niveau du message (C:50, E:40, W:30, I:20, D:10)
%(lineno)d Ligne où trouver l'appel à écriture dans le log. Relatif au fichier d'appel
%(module)s Nom du module ayant appelé l'écriture dans le log
%(msecs)d Temps d'exécution depuis le lancement du programme en millisecondes
%(message)s Le message à logger
%(name)s Le nom de l'utilisateur courant
%(pathname)s Chemin absolu du fichier ayant appelé l'écriture
%(process)d Le numéro du process courant
%(processName)s Le nom du process courant
%(thread)d L'ID du thread courant
%(threadName)s Le nom du thread courant
"""

"""
def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = True
    logger.
    return logger
"""
