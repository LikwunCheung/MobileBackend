from .base_setting import *

DEBUG = True

FILE_PATH = '/Users/likwuncheung/repos/file'

ALLOWED_HOSTS = ['*']

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_NAME = "session_id"
SESSION_COOKIE_SAMESITE = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mobile',
        'USER': 'mobile',
        'PASSWORD': 'mobile',
        'HOST': '52.187.104.237',
        'PORT': 8000,
        'CHARSET': 'utf8mb4',
        'CONN_MAX_AGE': 600,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]'
        },
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        'collect': {
            'format': '%(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 'default': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/root/logs/default.log',
        #     'maxBytes': 1024 * 1024 * 50,
        #     'formatter': 'simple',
        #     'encoding': 'utf-8',
        # },
        # 'error': {
        #     'level': 'ERROR',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/root/logs/error.log',
        #     'maxBytes': 1024 * 1024 * 50,
        #     'formatter': 'standard',
        #     'encoding': 'utf-8',
        # },
        # 'collect': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/root/logs/collect.log',
        #     'maxBytes': 1024 * 1024 * 50,
        #     'backupCount': 1,
        #     'formatter': 'collect',
        #     'encoding': "utf-8"
        # },
    },
    'loggers': {
        'django': {
            # 'handlers': ['default', 'console', 'error'],
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # 'collect': {
        #     'handlers': ['console', 'collect'],
        #     'level': 'INFO',
        # },
    }
}