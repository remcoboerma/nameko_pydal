import pydal
from nameko.extensions import DependencyProvider

# for sqlite: pip install pypiwin32 on windows!
# see http://nameko.readthedocs.org/en/stable/writing_extensions.html
# see http://nameko.readthedocs.org/en/stable/examples/index.html#travis

DB_URIS = 'database_uris'


class DalProvider(DependencyProvider):
    def __init__(self, define_model):
        """
        Create a new pydal depencency provider.
        Use the callback to define the database model on container start.

        :param define_model: a callback with the opened pydal connetion as a parameter.
        :return:
        """
        super(DalProvider, self).__init__()
        self.define_model = define_model

    def setup(self):
        """
        Read from database_uris section in the config file the service_name as a key
        :return:
        """
        db_config = self.container.config[DB_URIS][self.container.service_name]
        self.db_args = db_config['args']
        self.db_kwargs = db_config['kwargs']

    def start(self):
        self.db_connection = pydal.DAL(*self.db_args, **self.db_kwargs)
        if callable(self.define_model): self.define_model(self.db_connection)

    def get_dependency(self, worker_ctx):
        return self.db_connection

    def stop(self):
        self.db_connection.close()

    def kill(self):
        self.db_connection.rollback()

    def worker_result(self, worker_ctx, result=None, exc_info=None):
        """
        Called with the result of a service worker execution.

        Dependencies that need to process the result should do it here.
        This method is called for all Dependency instances on completion of any worker.

        Example: a database session dependency may flush the transaction
        :param worker_ctx:
        :param result:
        :param exc_info:
        :return:
        """
        if exc_info is not None:
            self.db_connection.rollback()
        else:
            self.db_connection.commit()

