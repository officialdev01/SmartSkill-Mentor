from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from pathlib import Path
from datetime import date, datetime
from functools import wraps
import sqlite3, os, csv, io

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key")
DB=Path(__file__).with_name("smartskill_advanced.db")
ADMIN_PIN=os.environ.get("ADMIN_PIN","2468")
CAREERS={
"Web Developer":["HTML","CSS","JavaScript","Git & GitHub","Flask"],
"Data Analyst":["Excel","SQL","Python","Pandas","Power BI"],
"Python Developer":["Python Basics","Functions & OOP","SQL","Flask","Git & GitHub"],
"UI/UX Designer":["Design Principles","Figma","Wireframing","Prototyping","Portfolio"]}
INFO={
"HTML":("HTML creates webpage structure with headings, paragraphs, links and forms.","https://developer.mozilla.org/en-US/docs/Web/HTML"),
"CSS":("CSS styles webpages with colors, spacing, layouts and typography.","https://developer.mozilla.org/en-US/docs/Web/CSS"),
"JavaScript":("JavaScript adds interaction and dynamic behaviour to websites.","https://developer.mozilla.org/en-US/docs/Web/JavaScript"),
"Git & GitHub":("Git tracks code changes and GitHub hosts code online.","https://docs.github.com/"),
"Flask":("Flask is a lightweight Python framework for web applications.","https://flask.palletsprojects.com/"),
"Excel":("Excel organizes data, formulas, charts and analysis.","https://support.microsoft.com/excel"),
"SQL":("SQL stores, retrieves and manages relational data.","https://www.w3schools.com/sql/"),
"Python":("Python is a readable general-purpose programming language.","https://docs.python.org/3/tutorial/"),
"Python Basics":("Learn variables, data types, conditions, loops and input/output.","https://docs.python.org/3/tutorial/"),
"Functions & OOP":("Functions organize reusable code; OOP models data and behaviour.","https://docs.python.org/3/tutorial/classes.html"),
"Pandas":("Pandas cleans, transforms and analyzes tabular data.","https://pandas.pydata.org/docs/"),
"Power BI":("Power BI creates interactive data reports and dashboards.","https://learn.microsoft.com/power-bi/"),
"Design Principles":("Design principles help create clear and usable interfaces.","https://www.nngroup.com/articles/ten-usability-heuristics/"),
"Figma":("Figma is a collaborative interface design and prototyping tool.","https://help.figma.com/"),
"Wireframing":("Wireframes show screen structure before detailed design.","https://www.nngroup.com/articles/wireframes/"),
"Prototyping":("Prototypes simulate how a product will work.","https://www.figma.com/resource-library/what-is-prototyping/"),
"Portfolio":("A portfolio presents your projects and skills.","https://www.behance.net/")}
QB={
"HTML":[("What does HTML stand for?",["HyperText Markup Language","HighText Machine Language","Hyper Tool Multi Language","Home Tool Markup Language"],0),("Largest standard heading tag?",["<head>","<h6>","<h1>","<title>"],2),("Image alternate text attribute?",["src","alt","href","title"],1),("Hyperlink tag?",["<link>","<a>","<p>","<img>"],1),("Visible page content is inside?",["<body>","<meta>","<head>","<style>"],0)],
"CSS":[("CSS stands for?",["Computer Style Sheets","Cascading Style Sheets","Creative Styling System","Colorful Style Syntax"],1),("Text color property?",["font-style","background","color","text-size"],2),("Selector for id main?",[".main","#main","main()","*main"],1),("Space inside element?",["margin","padding","border","outline"],1),("Flex container value?",["display:block","display:grid","display:flex","position:flex"],2)],
"JavaScript":[("Block-scoped variable keyword?",["var","let","define","dim"],1),("Strict equality operator?",["=","==","===","!="],2),("Select element by id?",["getElementById()","queryClass()","selectId()","getByName()"],0),("True/false data type?",["String","Number","Boolean","Array"],2),("Function keyword?",["func","function","method","def"],1)],
"Python":[("Python comment symbol?",["//","#","/*","--"],1),("Key-value collection?",["list","tuple","dict","set"],2),("Function keyword?",["function","fun","def","define"],2),("len('cat') returns?",["2","3","4","Error"],1),("Ordered and changeable collection?",["tuple","list","frozenset","str"],1)],
"Python Basics":[("Python comment symbol?",["//","#","<!--","**"],1),("Function keyword?",["func","def","function","make"],1),("Whole number type?",["int","str","list","dict"],0),("Loop over a sequence?",["if","for","try","class"],1),("Display output?",["input()","print()","len()","type()"],1)],
"Excel":[("Formula to add values?",["=ADD()","=SUM()","=TOTAL()","=PLUS()"],1),("Formula begins with?",["#","=","@","$"],1),("Arrange data in order?",["Sort","Wrap Text","Merge","Format Painter"],0),("Charts are used to?",["Delete data","Visualize data","Encrypt data","Rename cells"],1),("Cell address has?",["Column and row","Only row","Only sheet","Only formula"],0)],
"SQL":[("Retrieve data command?",["GET","OPEN","SELECT","FETCHALL"],2),("Filter rows clause?",["ORDER BY","WHERE","GROUP","SORT"],1),("Add a row command?",["INSERT","UPDATE","ALTER","CREATE"],0),("Unique row key?",["Foreign key","Primary key","Duplicate key","None"],1),("Count rows function?",["SUM()","TOTAL()","COUNT()","NUMBER()"],2)]}
DEFAULT=[("What helps you learn a technical skill?",["Regular practice","Avoiding practice","Only memorizing names","Skipping projects"],0),("A portfolio is?",["Collection of work samples","Computer cable","Database error","Password"],0),("When code fails, you should?",["Review and debug","Delete everything","Stop learning","Ignore it"],0),("Why are fundamentals important?",["Support advanced learning","Never used","Replace practice","Prevent projects"],0),("A good learning habit?",["Practice consistently","Study once yearly","Never revise","Avoid feedback"],0)]

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
 with db() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1),name TEXT NOT NULL,email TEXT DEFAULT '',career TEXT NOT NULL,created TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS skills(id INTEGER PRIMARY KEY AUTOINCREMENT,skill TEXT UNIQUE NOT NULL,completed INTEGER DEFAULT 0);
  CREATE TABLE IF NOT EXISTS quizzes(id INTEGER PRIMARY KEY AUTOINCREMENT,skill TEXT,score INTEGER,total INTEGER,created TEXT);
  CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,task_date TEXT,done INTEGER DEFAULT 0);
  CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY AUTOINCREMENT,message TEXT,created TEXT,is_read INTEGER DEFAULT 0);""")
  if not c.execute("SELECT id FROM profile WHERE id=1").fetchone():
   c.execute("INSERT INTO profile VALUES(1,'Student','','Web Developer',?)",(date.today().isoformat(),))
   for s in CAREERS["Web Developer"]: c.execute("INSERT OR IGNORE INTO skills(skill) VALUES(?)",(s,))
def notice(msg):
 with db() as c:c.execute("INSERT INTO notices(message,created) VALUES(?,?)",(msg,datetime.now().strftime("%d %b %Y %I:%M %p")))
def admin_only(f):
 @wraps(f)
 def w(*a,**k):
  if not session.get("admin"): flash("Admin PIN required.","warning"); return redirect(url_for("admin_login"))
  return f(*a,**k)
 return w
@app.context_processor
def common():
 with db() as c:n=c.execute("SELECT COUNT(*) n FROM notices WHERE is_read=0").fetchone()["n"]
 return {"unread":n}
@app.route("/")
def home():return redirect(url_for("dashboard"))
@app.route("/setup",methods=["GET","POST"])
def setup():
 with db() as c:p=c.execute("SELECT * FROM profile WHERE id=1").fetchone()
 if request.method=="POST":
  name=request.form.get("name","").strip(); email=request.form.get("email","").strip(); career=request.form.get("career","")
  if not name or career not in CAREERS:flash("Enter your name and select a career.","danger");return render_template("setup.html",p=p,careers=CAREERS)
  with db() as c:
   c.execute("UPDATE profile SET name=?,email=?,career=? WHERE id=1",(name,email,career));c.execute("DELETE FROM skills")
   for s in CAREERS[career]:c.execute("INSERT INTO skills(skill) VALUES(?)",(s,))
  notice(f"Welcome {name}. Your {career} roadmap is ready.");return redirect(url_for("dashboard"))
 return render_template("setup.html",p=p,careers=CAREERS)
@app.route("/dashboard")
def dashboard():
 with db() as c:
  p=c.execute("SELECT * FROM profile WHERE id=1").fetchone();skills=c.execute("SELECT * FROM skills ORDER BY id").fetchall()
  results=c.execute("SELECT * FROM quizzes ORDER BY id DESC LIMIT 5").fetchall();tasks=c.execute("SELECT * FROM tasks WHERE task_date=? ORDER BY done,id",(date.today().isoformat(),)).fetchall()
  attempts=c.execute("SELECT COUNT(*) n FROM quizzes").fetchone()["n"]
 total=len(skills);done=sum(x["completed"] for x in skills);percent=round(done*100/total) if total else 0
 return render_template("dashboard.html",p=p,skills=skills,results=results,tasks=tasks,total=total,done=done,percent=percent,attempts=attempts)
@app.route("/profile",methods=["GET","POST"])
def profile():
 with db() as c:p=c.execute("SELECT * FROM profile WHERE id=1").fetchone()
 if request.method=="POST":
  name=request.form.get("name","").strip();email=request.form.get("email","").strip()
  if name:
   with db() as c:c.execute("UPDATE profile SET name=?,email=? WHERE id=1",(name,email))
   notice("Student profile updated.");flash("Profile updated.","success")
  return redirect(url_for("profile"))
 return render_template("profile.html",p=p)
@app.route("/career",methods=["GET","POST"])
def career():
 with db() as c:current=c.execute("SELECT career FROM profile WHERE id=1").fetchone()["career"]
 if request.method=="POST":
  choice=request.form.get("career")
  if choice in CAREERS:
   with db() as c:
    c.execute("UPDATE profile SET career=? WHERE id=1",(choice,));c.execute("DELETE FROM skills")
    for s in CAREERS[choice]:c.execute("INSERT INTO skills(skill) VALUES(?)",(s,))
   notice(f"Career path changed to {choice}.");flash("Roadmap updated.","success")
  return redirect(url_for("dashboard"))
 return render_template("career.html",careers=CAREERS,current=current)
@app.route("/learn/<int:sid>")
def learn(sid):
 with db() as c:s=c.execute("SELECT * FROM skills WHERE id=?",(sid,)).fetchone()
 if not s:return redirect(url_for("dashboard"))
 desc,url=INFO.get(s["skill"],(f"Learn the fundamentals of {s['skill']} through practice.","https://www.google.com/search?q=tutorial"))
 return render_template("learn.html",s=s,desc=desc,url=url)
@app.route("/skill/<int:sid>/toggle",methods=["POST"])
def skill_toggle(sid):
 with db() as c:
  s=c.execute("SELECT * FROM skills WHERE id=?",(sid,)).fetchone()
  if s:
   val=1-s["completed"];c.execute("UPDATE skills SET completed=? WHERE id=?",(val,sid))
 if s:notice(f"{'Completed' if val else 'Reopened'} skill: {s['skill']}")
 return redirect(request.referrer or url_for("dashboard"))
@app.route("/quiz/<path:skill>")
def quiz(skill):return render_template("quiz.html",skill=skill,questions=QB.get(skill,DEFAULT))
@app.route("/quiz/<path:skill>/submit",methods=["POST"])
def quiz_submit(skill):
 qs=QB.get(skill,DEFAULT);score=0
 for i,q in enumerate(qs):
  try:score+=int(request.form.get(f"q{i}",-1))==q[2]
  except ValueError:pass
 with db() as c:c.execute("INSERT INTO quizzes(skill,score,total,created) VALUES(?,?,?,?)",(skill,score,len(qs),datetime.now().strftime("%d %b %Y %I:%M %p")))
 notice(f"{skill} quiz result: {score}/{len(qs)}")
 return render_template("quiz_result.html",skill=skill,score=score,total=len(qs))
@app.route("/leaderboard")
def leaderboard():
 with db() as c:
  rows=c.execute("SELECT skill,SUM(score) points,SUM(total) possible,COUNT(*) attempts FROM quizzes GROUP BY skill ORDER BY points DESC").fetchall()
  top=c.execute("SELECT * FROM quizzes ORDER BY 1.0*score/total DESC LIMIT 10").fetchall()
 return render_template("leaderboard.html",rows=rows,top=top)
@app.route("/planner",methods=["GET","POST"])
def planner():
 if request.method=="POST":
  title=request.form.get("title","").strip();d=request.form.get("task_date") or date.today().isoformat()
  if title:
   with db() as c:c.execute("INSERT INTO tasks(title,task_date) VALUES(?,?)",(title,d))
   notice(f"Study task added: {title}")
  return redirect(url_for("planner"))
 with db() as c:tasks=c.execute("SELECT * FROM tasks ORDER BY task_date DESC,id DESC").fetchall()
 return render_template("planner.html",tasks=tasks,today=date.today().isoformat())
@app.route("/task/<int:tid>/toggle",methods=["POST"])
def task_toggle(tid):
 with db() as c:c.execute("UPDATE tasks SET done=1-done WHERE id=?",(tid,))
 return redirect(url_for("planner"))
@app.route("/task/<int:tid>/delete",methods=["POST"])
def task_delete(tid):
 with db() as c:c.execute("DELETE FROM tasks WHERE id=?",(tid,))
 return redirect(url_for("planner"))
@app.route("/notifications")
def notifications():
 with db() as c:rows=c.execute("SELECT * FROM notices ORDER BY id DESC").fetchall();c.execute("UPDATE notices SET is_read=1")
 return render_template("notifications.html",rows=rows)
@app.route("/certificate")
def certificate():
 with db() as c:
  p=c.execute("SELECT * FROM profile WHERE id=1").fetchone();stat=c.execute("SELECT COUNT(*) total,COALESCE(SUM(completed),0) done FROM skills").fetchone()
 if not stat["total"] or stat["done"]!=stat["total"]:flash("Complete all roadmap skills to unlock the certificate.","warning");return redirect(url_for("dashboard"))
 return render_template("certificate.html",p=p,issued=date.today().strftime("%d %B %Y"))
@app.route("/admin")
def admin_login():return render_template("admin_login.html")
@app.route("/admin/verify",methods=["POST"])
def admin_verify():
 if request.form.get("pin")==ADMIN_PIN:session["admin"]=True;return redirect(url_for("admin_panel"))
 flash("Incorrect PIN.","danger");return redirect(url_for("admin_login"))
@app.route("/admin/panel")
@admin_only
def admin_panel():
 with db() as c:
  p=c.execute("SELECT * FROM profile WHERE id=1").fetchone();skills=c.execute("SELECT * FROM skills").fetchall();results=c.execute("SELECT * FROM quizzes ORDER BY id DESC").fetchall()
  stats={"quizzes":c.execute("SELECT COUNT(*) n FROM quizzes").fetchone()["n"],"tasks":c.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"]}
 return render_template("admin.html",p=p,skills=skills,results=results,stats=stats)
@app.route("/admin/skill/add",methods=["POST"])
@admin_only
def admin_add():
 s=request.form.get("skill","").strip()
 if s:
  with db() as c:c.execute("INSERT OR IGNORE INTO skills(skill) VALUES(?)",(s,))
  notice(f"Admin added skill: {s}")
 return redirect(url_for("admin_panel"))
@app.route("/admin/skill/<int:sid>/delete",methods=["POST"])
@admin_only
def admin_delete(sid):
 with db() as c:c.execute("DELETE FROM skills WHERE id=?",(sid,))
 return redirect(url_for("admin_panel"))
@app.route("/admin/export")
@admin_only
def admin_export():
 with db() as c:rows=c.execute("SELECT skill,score,total,created FROM quizzes ORDER BY id DESC").fetchall()
 out=io.StringIO();w=csv.writer(out);w.writerow(["Skill","Score","Total","Date"])
 for r in rows:w.writerow(list(r))
 res=make_response(out.getvalue());res.headers["Content-Disposition"]="attachment; filename=quiz_results.csv";res.headers["Content-Type"]="text/csv";return res
@app.route("/admin/logout")
def admin_logout():session.pop("admin",None);return redirect(url_for("dashboard"))
if __name__=="__main__":
 init_db();app.run(debug=True,host="127.0.0.1",port=5000)
