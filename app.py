import random
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
import pricescrap
from apscheduler.schedulers.background import BackgroundScheduler
from string import punctuation


app = Flask(__name__)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_HOST'] = db['mysql_host']
mysql = MySQL(app)




userd = ""
passd = ""
url1 = ""
@app.route("/")
def homepage():
    return render_template("website/homepage.html")

user1 = ""

@app.route("/admindash/<user>/<delete>", methods=['POST', 'GET'])
def admindash(user, delete):
    global user1
    user1 = user
   # print(user, delete)
    if delete == "0":
        email = user1
        con = mysql.connection.cursor()
        con.execute('select * from prod where email="%s";' % (email))
        rs = con.fetchall()  # fetches all data from database and stores in rs
        # all alphabets will just store the indexes of specfic data (site 0,image 1,link 2,3,4,.....)
        l = []  # whole data
        m = []  # image index
        s = []  # product link index
        si = []  # site name
        id = 1
        for row in rs:
            l.append(row[2])
            l.append(row[1])
            s.append(len(l) - 2)
            si.append(len(l) - 1)
            l.append(row[3])
            m.append(len(l) - 1)
            l.append(row[4])
            l.append(row[5])
            l.append(row[6])
            l.append(row[7])
            l.append("next")
        return render_template("website/admindash.html", data=l, l=len(l), m=m, s=s, s1=si, user=email)
    elif delete != 0:
        email = user1
        con = mysql.connection.cursor()
        con.execute('delete from prod where prodname="%s";' % (delete))
        mysql.connection.commit()
        con.execute('select * from prod where email="%s";' % (email))
        rs = con.fetchall()  # fetches all data from database and stores in rs
        # all alphabets will just store the indexes of specfic data (site 0,image 1,link 2,3,4,.....)
        l = []  # whole data
        m = []  # image index
        s = []  # product link index
        si = []  # site name
        id = 1
        for row in rs:
            l.append(row[2])
            l.append(row[1])
            s.append(len(l) - 2)
            si.append(len(l) - 1)
            l.append(row[3])
            m.append(len(l) - 1)
            l.append(row[4])
            l.append(row[5])
            l.append(row[6])
            l.append(row[7])
            l.append("next")
        return render_template("website/admindash.html", data=l, l=len(l), m=m, s=s, s1=si, user=email)

@app.route("/admin", methods=['POST', 'GET'])
def admin():
    usersss = []
    con = mysql.connection.cursor()
    con.execute('select * from user;')
    rs = con.fetchall()
    for row in rs:
        usersss.append(row[0])   #name
        usersss.append(row[1])   #email
        usersss.append(row[3])   #phone
    return render_template('website/admin.html', userss=usersss, l=len(usersss))


@app.route("/login", methods=['POST', 'GET'])
def login():
    try:
        if request.method == 'POST':
            log = request.form
            u = log['user']
            p = log['pas']
            if u == "" or p == "" :
                flash("!All fields are required")
                return render_template("website/login.html")
            elif u == "admin" and p == "admin":
                return redirect(url_for('admin'))
            else :
                cur = mysql.connection.cursor()
                cur.execute('select * from user where email="%s" and password="%s";'%(u, p))
                rs = cur.fetchall()
                if rs[0][1] == u and rs[0][2] == p :
                    global userd
                    global passd
                    userd = u
                    passd = p
                    return redirect(url_for('home'))
        elif request.method == 'GET':
            return render_template("website/login.html")
    except:
        flash("!Something went wrong , loginTry Again...")
        return render_template("website/login.html")

@app.route("/signup1", methods=['GET', 'POST'])
def signup1():
    if request.method == 'POST':
        details = request.form
        n = details['name']
        u = details['user']
        p = details['pas']
        cpas = details['cpas']
        m = details['mob']
        if n == "" or u == "" or p == "" or cpas == "" or m == "" :
            flash("!All fields are required")
            return render_template("website/signup1.html")
        else:
            if "@" not in u and ".com" not in u:
                flash("Enter Valid Email !!!!!!!!!")
                return render_template("website/signup1.html")
            if len(p) < 8 and len(p) > 12:
                flash("!Password should have atleast 8 characters and not more than 12 characters!")
                return render_template("website/signup1.html")
            if p != cpas:
                flash("!Password and Confirm password should be same")
                return render_template("website/signup1.html")
            if len(m) != 10:
                flash("Incorrect Mobile Number !!!!!!!!!!!!!!")
                return render_template("website/signup1.html")
            else:
                cur = mysql.connection.cursor()
                cur.execute('select email from user;');
                rs = cur.fetchall()
                for row in rs:
                    if u in row:
                        flash("Account Already Exists!!")
                        return render_template("website/signup1.html")
                rs =cur.execute('insert into user values("%s","%s","%s","%s");'%(n,u,p,m))
                mysql.connection.commit()
                return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template("website/signup1.html")




@app.route("/profile", methods=['POST', 'GET'])
def profile():

    global userd
    try:
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            cur.execute('select * from user where email="%s" and password="%s";'%(userd, passd))
            rs = cur.fetchall()
            user = rs[0][0]
            email = rs[0][1]
            pas = rs[0][2]
            mob = rs[0][3]
            return render_template("website/profile.html", user=user, email=email, mob=mob)
        elif request.method == 'POST':
            details = request.form
            n = details['name']
            u = details['user']
            m = details['mob']
            cur = mysql.connection.cursor()
            cur.execute('update user set name="%s",email="%s",phone="%s" where email="%s" and password="%s";' %(n, u, m, userd, passd))
            mysql.connection.commit()
            userd = u
            return render_template("website/profile.html", user=n, email=u, mob=m)
    except :
        flash("!Something went wrong , Try Again...")
        return render_template("website/profile.html", user=user, email=email, mob=mob)

site = ""
title = ""
price = ""
img = ""


@app.route("/home", methods=['POST', 'GET'])
def home():
    global title, price, img, site, userd, url1
    if request.method == 'POST':
        page = request.form
        try:
            url = page['search']
            url1 = url
            s, t, p, i, u = pricescrap.price(url)
            site, title, price, img, url1 = s, t, p, i, u
            print(s, i, t, p)
            flash(s)
            flash(i)
            flash(t)
            flash(p)
            return redirect(url_for('home', url=u))
        except :
            img1 = request.form[img]
            site1 = request.form[site]
            title1 = request.form[title]
            price1 = request.form[price]
            pr = price1[1:].replace(',','')
            dprice = request.form['dprice']
            u1 = request.args['url']

            con = mysql.connection.cursor()
            con.execute('insert into prod values("%s","%s","%s","%s","%s","%s","%s","%s")'%(userd, site1, u1, img1, title1, pr, dprice, pr))
            mysql.connection.commit()
            return redirect(url_for('dashboard', name='0', dprice='0'))
            #return redirect(url_for('track_price', site=site1,img=img1,title=title1,price=pr,dprice=dprice))
    elif request.method == 'GET':
        return render_template("website/newindex.html")

@app.route("/sites")
def sites():
    return render_template("website/sites.html")

@app.route("/services")
def services():
    return render_template("website/services.html")

@app.route("/about")
def about():
    return render_template("website/about.html")


@app.route("/home/track_price")
def track_price():
    site1 = request.args['site']
    img1 = request.args['img']
    title1 = request.args['title']
    price1 = request.args['price']
    dprice = request.args['dprice']
    flash(site1)
    flash(img1)
    flash(title1)
    flash(price1)
    flash(dprice)
    return render_template("website/track_price.html")


@app.route("/dashboard/<name>/<dprice>")
def dashboard(name, dprice):
    global userd
    if name == "0":
        email = userd
        con = mysql.connection.cursor()
        con.execute('select * from prod where email="%s";'%(email))
        rs = con.fetchall()  #fetches all data from database and stores in rs
        #all alphabets will just store the indexes of specfic data (site 0,image 1,link 2,3,4,.....)
        l = [] #whole data
        m = [] #image index
        s = [] #product link index
        si = [] #site name
        id = 1
        for row in rs:
            l.append(row[2]) #l[0]
            l.append(row[1])
            s.append(len(l)-2) #s[0]
            si.append(len(l)-1)
            l.append(row[3])
            m.append(len(l)-1)
            l.append(row[4])
            l.append(row[5])
            l.append(row[6])
            l.append(row[7])
            l.append("next")
        return render_template("website/dashboard.html", data=l, l=len(l),m=m, s=s, s1=si)
    elif name != 0:
        print("id="+name)
        email = userd
        con = mysql.connection.cursor()
        con.execute('delete from prod where prodname="%s" and dprice="%s";'%(name, dprice))
        mysql.connection.commit()
        con.execute('select * from prod where email="%s";' % (email))
        rs = con.fetchall()  # fetches all data from database and stores in rs
        # all alphabets will just store the indexes of specfic data (site 0,image 1,link 2,3,4,.....)
        l = []  # whole data
        m = []  # image index
        s = []  # product link index
        si = []  # site name
        id = 1
        for row in rs:
            l.append(row[2])
            l.append(row[1])
            s.append(len(l) - 2)
            si.append(len(l) - 1)
            l.append(row[3])
            m.append(len(l) - 1)
            l.append(row[4])
            l.append(row[5])
            l.append(row[6])
            l.append(row[7])
            l.append("next")
        return render_template("website/dashboard.html", name="0", dprice="0", data=l, l=len(l), m=m, s=s, s1=si)





@app.route("/forgetpass", methods=['POST', 'GET'])
def forgetpass():
    try:
        if request.method == 'POST':
            email = request.form['foremail']
            code = random.randint(111111, 999999)
            pricescrap.forgetpassmail(email, code)
            session['email'] = email
            session['code'] = str(code)
            return redirect(url_for('newpass'))
        elif request.method == 'GET':
            return render_template("website/forgetpass.html")
    except :
        flash("!Something went wrong , Try Again...")
        return render_template("website/forgetpass.html")


@app.route("/profile/newpass", methods=['POST', 'GET'])
def newpass():
    try:
        email = session['email']
        code = session['code']
        if request.method == 'POST':
            code1 = request.form['code']
            newp = request.form['pas']
            rnewp = request.form['cpas']
            if code == code1 and newp == rnewp:
                con = mysql.connection.cursor()
                con.execute('update user set password="%s" where email="%s"'%(newp, email))
                mysql.connection.commit()
                con.close()
                return redirect(url_for('login'))
            else:
                flash("!Something went wrong , Try Again...")
                return render_template("website/newpass.html")
        elif request.method == 'GET':
            return render_template("website/newpass.html")
    except :
        flash("!Something went wrong , Try Again...")
        return redirect(url_for('forgetpass'))





def schedule_track():
    with app.app_context():
        con = mysql.connection.cursor()
        con.execute("select * from prod;")

        rs = con.fetchall()
        if (rs):
            links = []
            for row in rs:
                links.append(row[2])
            for link in links:
                s, t, p, i, u = pricescrap.price(link)
                pr = p[1:].replace(',', '')
                con.execute('update prod set newprice="%s" where link="%s"'%(pr, link))
                mysql.connection.commit()
                con.close()



def track_price():
    with app.app_context():
        con = mysql.connection.cursor()
        con.execute('select * from prod;')
        rs = con.fetchall()
        if(rs):
            linkprice = []
            for row in rs:
                e = row[0]
                l = row[2]
                d = row[6]
                linkprice.append((l, d, e))
            for lp in linkprice:
                l1, d1, e1 = lp
                s, t, p, i, u = pricescrap.price(l1)
                pr = p[1:].replace(',', '')
                if float(d1) >= float(pr):
                    pricescrap.sendupdatemail(u, e1, t, pr)
        con.close()




schd = BackgroundScheduler(daemon=True)
schd.add_job(schedule_track, 'interval', minutes=1)
schd.add_job(track_price, 'interval', minutes=1)
# schd.add_job(sendmail, "interval", seconds=10)
schd.start()



if __name__ == "__main__":
    app.secret_key = "name11"
    app.run(debug=True)