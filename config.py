import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    '''Config settings class.'''
   

    SQLALCHEMY_DATABASE_URI= 'mysql://root:Pass@word123@localhost/Recruitize'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']


    SECRET_KEY = 'you-will-never-guess'
        