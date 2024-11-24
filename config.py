from flask import Flask
from flask_mysqldb import MySQL
import mysql.connector


app = Flask (__name__)
app.secret_key = 'doces'


#Conexão com o Banco
db = mysql.connector.connect(
    host="localhost",  
    user="root",
    password="guararema02",
    database="sitededoces"
)


app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 8000
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'guararema02'
app.config['MYSQL_DB'] = 'sitededoces'

mysql = MySQL(app)
