import os
from flask import Flask,g, redirect, render_template, request , session
import psycopg2

# handeling database
class database_connection:
    class check_connection:
        conn = psycopg2.connect(dbname='comm',
                                user='postgres',
                                password=2004,
                                host='127.0.0.1',
                                port=5432)
        try:
            conn
        except:
            print("[-] Database not connected")
    class dostuff:
        def check_data(username,password):
            conn = psycopg2.connect(dbname='comm',
                                user='postgres',
                                password=2004,
                                host='127.0.0.1',
                                port=5432)
            curr = conn.cursor()
            curr.execute(f''' Select * from users where username='{username}' and password='{password}'; ''')
            data = curr.fetchall()
            conn.commit()
            # database_connection.check_connection.conn.close()
            return data
        def insert_data(query):
            conn = psycopg2.connect(dbname='comm',
                                user='postgres',
                                password=2004,
                                host='127.0.0.1',
                                port=5432)
            curr = conn.cursor()
            curr.execute(query)
            conn.commit()
            # database_connection.check_connection.conn.close()s
        def check_data_inside_table(query):
            conn = psycopg2.connect(dbname='comm',
                                user='postgres',
                                password=2004,
                                host='127.0.0.1',
                                port=5432)
            curr = conn.cursor()
            curr.execute(query)
            data = curr.fetchall()
            conn.commit()
            return data
#flask app
app = Flask('__name__')
app.secret_key = os.urandom(24)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user',None)
        username = request.form['username']
        password = request.form['password']
        data = database_connection.dostuff.check_data(username,password)
        print(data)
        if len(data) != 0:
            if data[0][1] == password:
                session['user'] = request.form['username']
                return redirect('/home')
            else:
                return redirect('/')
        else:
            if username == '' or password == '':
                return redirect('/')
            else:
                query1 = f''' insert into users values('{username}','{password}')'''
                query2 = f''' create table user_{username}(s_no varchar PRIMARY KEY,date date,expense varchar,amount int,category varchar);'''
                database_connection.dostuff.insert_data(query1)
                database_connection.dostuff.insert_data(query2)
                return redirect('/')
            
    else:
        return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def protected():
    if request.method == 'POST':
        if g.user==session['user']:
                date = request.form['date']
                expense = request.form['expense']
                amount = request.form['amount']
                category = request.form['category']
                query1 = f'''select s_no from user_{g.user}'''
                s_no = database_connection.dostuff.check_data_inside_table(query1)
                if s_no == []:
                    s_no = 0
                else:
                    s_no = int(s_no[-1][0])+1
                query = f''' insert into user_{g.user} values({s_no},'{date}','{expense}','{amount}','{category}'); '''
                database_connection.dostuff.insert_data(query)
                return render_template('addexp.html',user=g.user)
        else:
            return render_template('addexp.html',user=g.user)    
    else:
        if g.user==session['user']:
            return render_template('addexp.html',user=g.user)
        else:
            return redirect('/')

@app.route('/fetch')
def fetch_data():
    query = f''' select * from user_{g.user}'''
    data = database_connection.dostuff.check_data_inside_table(query)
    lenofdata = len(data)
    listocolumns = ['s_no','date','expense','amount']
    query = f'''select sum(amount) from user_{g.user}; '''
    total_karcha = database_connection.dostuff.check_data_inside_table(query)
    return render_template('fetched.html',data=lenofdata,founddata=data,listocolumns=listocolumns,karcha=total_karcha[0][0])
@app.route('/del',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        if g.user == session['user']:
            expense_name = request.form['expense']
            s_no = int(request.form['s_no'])
            query = f''' delete from user_{g.user} where expense='{expense_name}' and s_no='{s_no}';  '''
            database_connection.dostuff.insert_data(query)
            return redirect('/del')
        else:
            return redirect('/')
    else:
        if g.user == session['user']:
            return render_template('deleted.html')
        else:
            return redirect('/')

@app.before_request
def beforereq():
    g.user = None
    if 'user' in session:
        g.user = session['user']

if __name__ == '__main__':
    app.run(debug=True)
