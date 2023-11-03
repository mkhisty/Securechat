from flask import Flask,request,render_template,redirect,url_for,session
from flask_socketio import SocketIO
import json
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
socketio = SocketIO(app)
with open(r"C:\Users\Malhar\OneDrive\Desktop\Python and Stuff\Web\Flask\Chat\accounts.json") as a :
    accounts = json.load(a)
with open(r"C:\Users\Malhar\OneDrive\Desktop\Python and Stuff\Web\Flask\Chat\contacts.json") as c :
    contacts = json.load(c)
with open(r"C:\Users\Malhar\OneDrive\Desktop\Python and Stuff\Web\Flask\Chat\chatdata.json") as ch :
    chatdata = json.load(ch)
def is_authenticated(u):
    try:
        if session["user_id"]==u and session["auth"]=="True":
            return True
    except:
        return False
    return False
def gethistory(chatid):
    strng =r"C:\Users\Malhar\OneDrive\Desktop\Python and Stuff\Web\Flask\Chat\chathistory\ "+str(chatid)
    strng.replace(" ","")
    chathistory = open(strng+".txt", "r")
    historystring = chathistory.read()
    hs = historystring
    chathistory.close()
    c = 0
    messages = []
    datetimes = []
    mediadata = []
    text = []
    people =[]
    for i in range(hs.count(">>|<<")):
        c+=1
        index = hs.index(">>|<<")
        messages.append(hs[0:index])
        end = len(hs)+1
        hs = hs[index+5 : end]
    for j in range(len(messages)):
        messagestring = messages[j]
        text.append(messagestring[0:messagestring.index("<<|>>")])
        messagestring = messagestring[messagestring.index("<<|>>")+5:len(messagestring)+1]
        mediadata.append(messagestring[0:messagestring.index("<<|>>")])
        messagestring = messagestring[messagestring.index("<<|>>")+5:len(messagestring)+1]
        datetimes.append(messagestring[0:messagestring.index("<<|>>")])
        messagestring = messagestring[messagestring.index("<<|>>")+5:len(messagestring)+1]
        people.append(messagestring[0:len(messagestring)+1])

    return [datetimes,mediadata,text,people]
@app.route("/login", methods=['GET', 'POST'])
def home():
    if request.method=="POST":
        try:
            username = request.form['usrnm']
            password = request.form["password"]
            if accounts[username][0]==password:
                session['user_id'] = username
                session["auth"] = "True"
                return redirect("/lobby?usrnm="+username)
        except: 
            return render_template("login.html")        
    return render_template("login.html")
@app.route("/lobby", methods=['GET', 'POST'])
def lobby():
    if is_authenticated(request.args.get("usrnm")):
        mycontacts = contacts[request.args.get("usrnm")].copy()
        contactnames = []
        for i in range(0,len(mycontacts)):
            if len(chatdata[mycontacts[i]])>2:
                contactnames.append(mycontacts[i])
            else:
                sub = chatdata[mycontacts[i]].copy()
                sub.remove([request.args.get("usrnm")])
                contactnames.append(sub[0][0])
        return render_template("lobby.html",contacts = contactnames)
    else:
        return redirect("/login")
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    elements = gethistory(request.args.get("chatid"))
    datetimes = elements[0]
    mediadata = elements[1]
    text = elements[2]
    people = elements[3]
    if is_authenticated(request.args.get("usrnm")):
        return render_template("chat.html",nom = len(datetimes),datetimes = datetimes,mediadata = mediadata, text = text, people =people )
    return redirect("/login")
@socketio.on('sessionstarted')
def setup(json, methods=['GET', 'POST']):
    username = json["usrnm"]
    chatid = json["chatid"]
    index = chatdata[chatid].index([username])
    chatdata[chatid][index].append(request.sid)

    socketio.emit('serversetup', request.sid,room = chatdata[json["chatid"]][index][1])
@socketio.on('sessionended')
def cleanup(json, methods=['GET', 'POST']):
    username = json["usrnm"]
    chatid = json["chatid"]
    index = chatdata[chatid].index([username,json["sid"]])
    chatdata[chatid][index].pop()
@socketio.on('my event')
def sendmessage(json, methods=['GET', 'POST']):
    for i in range(0,len(chatdata[json["chatid"]])):
        try:
            socketio.emit('my response', json,room = chatdata[json["chatid"]][i][1])
    
        except:
            pass
    chathistory = open("chathistory/"+str(json["chatid"])+".txt", "a")
    chathistory.write(str(json["message"])+"<<|>>"+str(json["mediadata"])+"<<|>>"+str(json["datetime"])+"<<|>>"+str(json["user_name"])+">>|<<")
    print(json)
    chathistory.close()
if __name__ == '__main__':
    socketio.run(app, debug=True,host= '0.0.0.0')
