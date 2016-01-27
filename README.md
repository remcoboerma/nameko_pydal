# Pydal for Nameko
Pydal extension for Nameko. 

As a longtime [Web2py](http://www.web2py.com/) user I really appreciate the [DAL](https://github.com/web2py/pydal). 
Which fortunately now is a standalone library. Having just learnt about [nameko](https://github.com/onefinestay/nameko) 
the match seems perfect. 

> **Not all supported database drivers will work**. Nameko uses the [eventlet](http://eventlet.net/) library and many
of the drivers probably aren't compatible. Please share your findings in a ticket or comment to help others know what
issues you ran into.

# Usage

```python
from nameko.rpc import rpc, RpcProxy
from pydal_extension import DalProvider
from pydal import Field
from datetime import datetime 


def define_model(db):
    db.define_table('something',
                    Field('foo'),
                    Field('ts','string',length=26+6,default=datetime.now().isoformat()) # store timestamps as strings
    )

class pydaltest(object):
    name = 'pydal_test'

    db = DalProvider(define_model)

    @rpc
    def add(self, value):
        self.db.something.insert(foo=value)

    @rpc
    def get_all(self):
        db, id = self.db, self.db.something.id
        sub_select = db(id > 0)._select(id.max())
        cnt = db(id > 0).count()
        newest_record = db(id.belongs(sub_select)).select().first().as_dict()
        return cnt, newest_record
```

Include the pydal `pydal.DAL(...)` object as a dependency using the `DalProvider`. It will open the database based on 
parameters in the config file. See [Config file additions](#config-file-additions) below for details. 

The `define_model` callback parameter of `DalProvider` lets you define you database model using the connection passed to 
the callback. When a new worker is spawned, it will receive a connection from the pool and the model is applied, 
just like in `web2py`. Connection pooling is included in `pydal`. This will automatically provide the connections
needed for the workers. 

# Config file additions
The `DalProvider` knows to which service it is bound. It will use the `.name` of the service to lookup the `args`
and `kwargs` applied to the `DAL` constructor from the configuration. Here is an example for a simple sqlite dabase 
with some keyword parameters set to the default values, purely for illustrative purposes. You see `database_uris` as 
the root of this configuration. It is a dictionary with the service name as a key and a dictionary as value. This latter
dictionary contains two keys: `args` and `kwargs` . Both are applied to the `DAL` constructor like `DAL(*args,**kwargs)`. 
Thus you have all freedom to setup the connection parameters as required. 
(Probably this is useful if you use a larger number of workers, otherwise they will be waiting for a 
new connection from the pool.) 

**Mind the `-` in front of `sqlite://`.**  
The `args` holds a `list`, it isn't just a string. It's a list of strings. 

```yaml 
database_uris:
    pydal_test:
      args:
        - sqlite://somedb.sqlite
      kwargs:
        db_codec : UTF-8
        migrate : true
```
