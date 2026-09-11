import os


class Config:
    MONGO_URI = os.environ["MONGO_URI"]


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
