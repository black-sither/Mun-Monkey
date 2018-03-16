from flask import Flask,render_template,request,session,redirect,json,jsonify
import os
from flask_socketio import SocketIO,emit,send,join_room,leave_room
from flask_mysqldb import MySQL
from flask_session import Session
import pickle
app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'munlogindb'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
mysql=MySQL(app)
socketio = SocketIO(app,manage_session=False)
ebchits=[]
usar={}
lgcnt=0
messlog={}
try:
    with open('mess.pkl','rb') as f:
        messlogbefore = pickle.load(f)
        messlog=messlogbefore
        #print(messlog)
    with open('ebchits.pkl','rb') as y:
        ebchits=pickle.load(y)
except EOFError:
    print('file is empty..')

@app.route('/session', methods=['GET', 'POST'])
def session_access():
    if request.method == 'GET':
        return jsonify({
            'session': session.get('value', '')
        })
    data = request.get_json()
    if 'session' in data:
        session['value'] = data['session']
        return ''

@app.route('/',methods=['GET','POST'])
def test():
     if request.method=="POST":
         conn=mysql.connection.cursor()
         passw=request.form['password']
         user=request.form['username']
         conn.execute("SELECT * from logins where password=%s and username=%s",[passw,user])
         row=conn.fetchone()
         if row:
             #session['Username']=user
             #lgcnt +=1
             #if user=="aditya":
                 #return render_template('index.html')
             #else:
             if row[3] =='EB':
                 return render_template('EBFinal.html')
             else:
                 return render_template('DelApps.html')
             #print("user logged in" + request.sid)
         else:
             #return render_template("")

             return "Username and/or password incorrect."

         #return request.form['username'] + " logged in"
     return render_template("login.html")
#@socketio.on('message')
#def handlemessage(msg):
    #print("Message:" + msg)
    #send(msg,broadcast=True)
#@socketio.on('connect')
#def test_connect():
    #emit('my response', {'data': 'Connected'})
    #print("connected to user is" + request.sid)

@socketio.on('connect')
def test_connect():
    #emit('my response', {'data': 'Connected'})
    print("")
@socketio.on('roomc')
def showroomconnect():
    print("Sid here" + request.sid)
@socketio.on('connect',namespace="/reg")
def hello():
    print('')#'User:' + 'msg' + ' request:' + request.sid)

@socketio.on('regi',namespace="/reg")
def registeruser(user):
    #print('User:' + msg + ' request:' + request.sid)
    usar[user]=request.sid
    if user not in messlog.keys():
        messlog[user]={}
    print("registered user: " + user +" with sid:" +usar[user])
    #print(messlog)

@socketio.on('sendmess')
def sendi(obj):
    if obj['message'].find('<')!=-1 or obj['message'].find('>')!=-1:
        print(session.get('value', '') +" maybe logged as " +obj['sender']+ "tried to change html");
    elif obj['sender'] ==session.get('value', ''):
        recip=obj['rece']
        sendsid=usar[recip]
        mess=obj['message']
        sender=obj['sender']
        payload={'sender':sender,'message':mess}
        print('Sender: '+sender +'  Receiver:  ' + recip + ' msg:' + mess + ' sid:' + sendsid)
        emit('new_message',payload,room=sendsid)
    else:
        print('user:' + session.get('value','') +"tried 2 logins from the same device")

@socketio.on('updatelogme')
def upd(obj):
    if obj['sender']==session.get('value', ''):
        recip=obj['rece']
        mess=obj['message']
        sender=obj['sender']
        messlog[sender].setdefault(recip,[]).append(mess)
@socketio.on('updatelogot')
def upd1(obj):
    if obj['rece']==session.get('value',''):
        recip=obj['rece']
        mess=obj['message']
        sender=obj['sender']
        messlog[sender].setdefault(recip,[]).append(mess)

@socketio.on('refchats',namespace='/reg')
def retchats(us):
    emit('prechits',ebchits,room=usar[us])
    emit('prevchats',messlog[us],room=usar[us])

@socketio.on('GetOthers',namespace='/reg')
def senduserlist(usur):
    #print("Get others,registered user:" + usur +"with sid:" +request.sid)
    key=list(usar.keys())
    l=len(key)
    payload={'key':key,'len':l}
    emit('GetUserList',payload,broadcast=True)

@socketio.on('savelog')
def saving():
    with open('mess.pkl','wb') as f:
        pickle.dump(messlog,f)
    with open('ebchits.pkl','wb') as y:
        pickle.dump(ebchits,y)
    print("saving chat logs..")

@socketio.on('ebchit')
def chit(pay):
    thechit=[pay['rece'],pay['message'],pay['sender'],pay['time']]
    ebchits.append(thechit)
    emit('chits',thechit,broadcast=True)



if __name__=="__main__":
    socketio.run(app, host='0.0.0.0', port=8083)
