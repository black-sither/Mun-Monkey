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
    with open('ebchits.pkl','rb') as y:
        ebchits=pickle.load(y)
except EOFError:
    print('file is empty..')

@app.route('/',methods=['GET','POST'])
def test():
    if request.method=="POST":
        conn=mysql.connection.cursor()
        passw=request.form['password']
        user=request.form['username']
        conn.execute("SELECT * from logins where password=%s and username=%s",[passw,user])
        row=conn.fetchone()
        if row:
            session['user']=user
            if row[3] =='EB':
                return render_template('EBFinal.html')
            else:
                return render_template('DelApps.html')
        else:
             return "Username and/or password incorrect."
    return render_template("login.html")


@socketio.on('roomc')
def showroomconnect():
    print("Sid here" + request.sid)
@socketio.on('connect',namespace="/reg")
def hello():
    print('')

@socketio.on('regi',namespace="/reg")
def registeruser(user):
    usar[session.get('user')]=request.sid
    if user not in messlog.keys():
        messlog[user]={}
    print("registered user: " + user +" with sid:" +usar[user] + "and session:" + session.get('user'))

@socketio.on('sendmess')
def sendi(obj):
    if obj['message'].find('<')!=-1 or obj['message'].find('>')!=-1:
        print(session.get('user') +" maybe logged as " + obj['sender'] + "tried to change javascript...");
    elif obj['sender'] ==session.get('user'):
        recip=obj['rece']
        try:
            sendsid=usar[recip]
        except KeyError:
            print("Somehow i am executed...")
            emit('Usrlgout',room=usar[session.get('user')])
        mess=obj['message']
        sender=obj['sender']
        payload={'sender':sender,'message':mess,'eb':obj['eb']}
        emit('new_message',payload,room=sendsid)
        print('Sender: '+ sender +'  Receiver:  ' + recip + ' msg:' + mess + ' sid:' + sendsid)
        emit('prevchats',messlog[recip],room=sendsid)
        emit('prechits',ebchits,broadcast=True)
    else:
        print('user:' + session.get('user') + "tried to change his cookie value" + "new cookie value is:" + obj['sender'])

@socketio.on('updatelogme')
def upd(obj):
    if obj['sender']==session.get('user'):
        recip=obj['rece']
        mess=obj['message']
        sender=obj['sender']
        messlog[sender].setdefault(recip,[]).append(mess)
@socketio.on('updatelogot')
def upd1(obj):
    if obj['rece']==session.get('user'):
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
