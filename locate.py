import mysql.connector
import os
print(os.path.join(os.path.dirname(mysql.connector.__file__), 'plugins'))