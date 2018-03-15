from flask import Flask, render_template,request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'munlogindb'
mysql=MySQL(app)
socketio=SocketIO(app)
@app.route('/',methods=['POST','GET'])
def test():
	conn=mysql.connection.cursor()
	for i in range(0,100):
		conn.execute("insert into logins values(user"+str(i)+",pass+"+str(i)+",'country"+str(i)+,' ');")
		mysql.connection.commit()

if __name__=="__main__":
	socketio.run(app)
