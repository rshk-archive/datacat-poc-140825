import os
import urlparse

from datacat.web import app
from datacat.db import create_tables, connect


host = os.environ.get('HOST', '127.0.0.1')
port = int(os.environ.get('PORT', 8000))

db_url = urlparse.urlparse(os.environ['DATABASE'])
app.config['DATABASE'] = {
    'database': db_url.path.split('/')[1],
    'user': db_url.username,
    'password': db_url.password,
    'host': db_url.hostname,
    'port': db_url.port or 5432,
}

try:
    create_tables(connect(**app.config['DATABASE']))
except:
    pass
app.run(debug=True, host=host, port=port)
