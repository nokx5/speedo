import os
from alembic.config import Config
from alembic import command


def run_alembic():

    # set the paths values
    root_directory = os.path.dirname(__file__)
    alembic_directory = os.path.join(root_directory)
    ini_path = os.path.join(root_directory, "..", "alembic.ini")

    # create Alembic config and feed it with paths
    config = Config(ini_path)
    config.set_main_option("script_location", alembic_directory)

    # prepare and run the command
    revision = "head"
    sql = False
    tag = None
    # command.stamp(config, revision, sql=sql, tag=tag)

    # upgrade command
    command.upgrade(config, revision, sql=sql, tag=tag)
