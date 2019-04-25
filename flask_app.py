from flask import Flask, render_template, request, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = b'*ayfaug76t^Y5T6y6r'

@app.route('/')
def main():
	conn = sqlite3.connect("userinfo.db")
	c = conn.cursor()
	s = "SELECT * from news"
	c.execute(s)
	s = c.fetchall()
	c.close()
	conn.close()
	return render_template("news.html",s=s)

@app.route('/login',methods=["GET","POST"])
def login():
	if request.method=="GET": return render_template("login.html")
	elif request.method == "POST":
		conn = sqlite3.connect("userinfo.db")
		c = conn.cursor()
		s = "SELECT email, password, user_id from users"
		login = False
		c.execute(s)
		uid = ''
		for x in c.fetchall():
			if request.form['email'] == x[0] and request.form['password'] == x[1]:
				login = True
				uid = x[2]
		c.close()
		conn.close()
		if login == True:
			session['id'] = uid
			return render_template("logincomplete.html")
		elif login == False:
			return render_template("loginfailed.html")

def create_user_id():
	aconn = sqlite3.connect("userinfo.db")
	ac = aconn.cursor()
	while True:
		opts = [i for i in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890']
		# 8 character long random hash
		t_id = "".join([random.choice(opts) for i in range(8)])
		s = "SELECT user_id from users where user_id = '" + t_id + "'"
		ac.execute(s)
		if len(ac.fetchall()) == 0:
			return t_id

# Criteria for valid account:
# Firstname: Only letters or hyphens, capital or lowercase
# Lastname: Only letters or hyphens, capital or lowercase
# securityquestion: Honestly we should just have a bunch of presets. I'm (Carter) not a huge fan of security questions, I would just prefer to have an email password reset.
# securityquestionanswer: Alphanumeric + special characters not including '" and \
# password: Alphanumeric + special characters not including '" and \
# email: valid email format... *******@*****.***
@app.route('/createanaccount',methods=["GET","POST"])
def createanaccount():
	if request.method=="GET":
		return render_template('createaccount.html',error='')
	elif request.method=="POST":
		nid = create_user_id()
		conn = sqlite3.connect("userinfo.db")
		c = conn.cursor()
		email = request.form['email']
		parts = email.split('@')
		if len(parts) != 2:
			return render_template('createaccount.html',error='email')
		if len(parts[1].split('.')) < 2:
			return render_template('createaccount.html',error='email')
		password = request.form['password']
		if '\'' in password or '\\' in password or '"' in password:
			return render_template('createaccount.html',error='password')
		namechars = [i for i in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM-']
		fname = request.form['FN']
		lname = request.form['LN']
		cond = False
		for i in fname:
			if i not in namechars:
				cond = True
		for i in lname:
			if i not in namechars:
				cond = True
		if cond:
			return render_template('createaccount.html',error='names')
		sql = "INSERT into users (user_id, email, password, Firstname, Lastname) values ('"+ str(nid) + "', '" + str(email) + "', '" + str(password) + "', '" + str(fname) + "', '" + str(lname) + "')"
		print(sql)
		c.execute(sql)
		conn.commit()
		c.close()
		conn.close()
		
		return render_template('accountcreated.html')

@app.route('/testdata')
def testdata():
    conn = sqlite3.connect("userinfo.db")
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    c.close()
    conn.close()
    a = "\n".join([" ".join([str(j) for j in i]) for i in data])
    return a
@app.route('/viewaccountinfo')
def viewaccountinfo():
	return render_template('viewcarteraccountinfo.html')

@app.route('/verifyid',methods=['POST'])
def verifyid():
	secure_hash = 'LOGANisHeckaGR4NNY!lma0'
	check_id = request.form['id']
	sent_hash = request.form['hash']
	if sent_hash == secure_hash:
		s = "SELECT * FROM users WHERE user_id = ?"
		conn = sqlite3.connect("userinfo.db")
		c = conn.cursor()
		c.execute(s)
		a = [i for i in c.fetchall()]
		c.close()
		conn.close()
		if len(a) == 1:
			return "VALID"
		else:
			return "INVALID"
	else:
		return "INVALID"

@app.route('/transaction',methods=['POST'])
def transaction():
	sender = request.form['sender']
	reciever = request.form['receiver']
	amount = request.form['amount']
	conn = sqlite3.connect("userinfo.db")
	c = conn.cursor()
	s = "SELECT balance from users where user_id = " + sender
	c.execute(s)
	a = c.fetchall()
	if len(a) != 1:
		#TODO: Update transaction status
		return "DENIED"
	a = float(a[0][0])
	if a < float(amount):
	    #TODO: Update transaction status
	    return "DENIED"
	#CONSIDER: Some taxation system that just burns money, counteract inflation.
	s = "UPDATE users SET balance = ? WHERE user_id = " + sender
	c.execute(s,(str(a-float(amount)),))
	s = "SELECT balance from users where user_id = ?"
	c.execute(s,(reciever,))
	b = c.fetchall()[0][0]
	s = "UPDATE users SET balance = ? WHERE user_id = ?"
	print(s)
	c.execute(s,(str(b+float(amount)),reciever))
	conn.commit()
	c.close()
	conn.close()
	# TODO: Update transaction status
	return "APPROVED"