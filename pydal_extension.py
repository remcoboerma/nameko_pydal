from __future__ import print_function
import pydal
from nameko.extensions import DependencyProvider

# import threading
# TL = THREAD_LOCAL = threading.local()
# import uuid

# for sqlite: pip install pypiwin32 on windows!
# see http://nameko.readthedocs.org/en/stable/writing_extensions.html
# see http://nameko.readthedocs.org/en/stable/examples/index.html#travis

DB_URIS = 'database_uris'


class DalProvider(DependencyProvider):
    def __init__(self, define_model):
        """
        Create a new pydal depencency provider.
        Use the callback to define the database model on container start.

        :param define_model: a callback with the opened pydal connetion, other_args as parameters
        :return:
        """
        super(DalProvider, self).__init__()
        self.define_model = define_model
        # print('DalProvider::__init__')


    def worker_setup(self, worker_ctx):
        """
        Read from database_uris section in the config file the service_name as a key
        :return: db_connection
        """
        # thread_id = uuid.uuid4()
        # TL.id = thread_id
        # print('DalProvider::worker_setup', getattr(TL,'id','?'))
        db_config = self.container.config[DB_URIS][self.container.service_name]
        self.db_args = db_config['args']
        self.db_kwargs = db_config['kwargs']
        self.other_args = db_config.get('other_args',{})
        worker_ctx.db_connection = pydal.DAL(*self.db_args, **self.db_kwargs)
        if callable(self.define_model):
            self.define_model(worker_ctx.db_connection, self.other_args)

    def get_dependency(self, worker_ctx):
        if not hasattr(worker_ctx,'db_connection'):
            self.worker_setup(worker_ctx)
        return worker_ctx.db_connection

    def worker_teardown(self, worker_ctx):
        # print('DalProvider::worker_teardown', getattr(TL,'id','?'))
        try:
            worker_ctx.db_connection.close()
        except:
            pass


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
        # print('DalProvider::worker_result')
        if exc_info is not None:
            try:
                worker_ctx.db_connection.rollback()
            except:
                pass
        else:
            try:
                worker_ctx.db_connection.commit()
            except:
                pass

