from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
app = Flask(__name__)
db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql=MySQL(app)
@app.route('/', methods=['GET','POST'])
def index():
    if request.method=='POST':
       studentdetails=request.form
       name=studentdetails['name']
       email=studentdetails['email']
       GREScore=studentdetails['GRE Score']
       TOEFLScore=studentdetails['TOEFL Score']
       UniversityRating=studentdetails['University Rating']
       sop=studentdetails['SOP']
       lor=studentdetails['LOR']
       cgpa=studentdetails['CGPA']
       Research=studentdetails['Research']
       cur=mysql.connection.cursor()
       cur.execute("INSERT INTO univ_eligi(name, email,GRE Score,TOEFL Score,University Rating,SOP,LOR,CGPA,Research) VALUES(%s, %s,%d,%d,%d,%d,%d,%d,%d)",(name, email,GREScore,TOEFLScore,UniversityRating,sop,lor,cgpa,Research))
       mysql.connection. commit()
       cur.close()
       return 'your details has been submitted successfully'
    return render_template('index.html')
if __name__=='__main__':
    app.run(debug=True)   