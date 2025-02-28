# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from questions import questions
import numpy as np
import datetime
import os
import math
import random


app = Flask(__name__)
#データベース設定

class Base(DeclarativeBase):
    pass
db=SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY']=os.urandom(24)
db.init_app(app)
migrate=Migrate(app,db)
login_manager=LoginManager()
login_manager.init_app(app)

#Userモデルの定義
class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str]= mapped_column(String(50), unique=True, nullable=False)
    password:Mapped[str] = mapped_column(db.String(255),nullable=False)

    progress=relationship("LearningProgress",back_populates="user",lazy=True)
    topics=relationship("Topic",back_populates="user")

class Topic(db.Model):
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True, nullable=False)
    user_id: Mapped[int]=mapped_column(Integer, ForeignKey('user.id'))

    user=relationship("User",back_populates="topics")
    progress=relationship("LearningProgress", back_populates="topic")

class LearningProgress(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey('topic.id'))
    date_learned: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    user=relationship("User", back_populates="progress")
    topic=relationship("Topic", back_populates="progress")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#User一覧の表示
@app.route("/")
def main():
    return render_template("application.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('quiz'))
        else:
            error_message = "ユーザー名またはパスワードが間違っています。"
            return render_template('login.html', error=error_message)
    return render_template('login.html')
        
@app.route("/tweets")
def tweets():
    return render_template("tweets.html")


@app.route("/users")
def user_list():
    users=db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("user/list.html",users=users)

#ユーザーの作成
@app.route('/user/signup', methods=['GET','POST'])
def signup():
    if request.method=="POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        #重複エラー処理
        if User.query.filter_by(username=username).first():
            error_message="このユーザー名はすでに使用されています"
            return render_template('user/signup.html', error=error_message)
        elif User.query.filter_by(email=email).first():
            error_message="このメールアドレスはすでに登録されています"
            return render_template('user/signup.html',error=error_message)
        #新規ユーザー作成
        user=User(username=username,email=email,password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_list'))
    else:
        return render_template('/user/signup.html')

#ユーザー詳細
@app.route("/user/<int:id>")
def user_detail(id):
    user=db.get_or_404(User,id)
    return render_template("user/detail.html",user=user)

def select_question(weights):
        candidates=[int(i) for i, W in weights.items() if float(W) >= 0.5]
        if candidates:
            return random.choice(candidates)
        else:
            return random.randint(0, len(questions) - 1)
        
@app.route('/quiz',  methods=['GET','POST'], endpoint='quiz')

              
def quiz():
    if 'question_weights' not in session:
        session['question_weights'] = {str(i) : 0.5 for i in range(len(questions))}

    if 'current_question' not in session:
        session['current_question'] = select_question(session['question_weights'])
        
    current_question_index = str(session['current_question'])

    current_question = questions[int(current_question_index)]

    if request.method=='POST':
        selected_answer=request.form.get('answer')
        correct_answer = current_question["answer"]

        if selected_answer==correct_answer:
            feedback="正解です！"
            session['question_weights'][str(current_question_index)] -= 0.1
        else:
            feedback="不正解です!"
            session['question_weights'][str(current_question_index)] += 0.2
        
        session['question_weights'][current_question_index]=max(0, min(1,session['question_weights'][current_question_index]))

        next_question = select_question(session['question_weights'])
        session['current_question'] = next_question
        explanation = current_question["explanation"]

        
        session.modified=True

        return render_template('quiz.html',question = questions[next_question], feedback = feedback, explanation = explanation)
        
    return render_template('quiz.html', question = questions[int(session['current_question'])])



@app.route("/user/<int:id>/delete",methods=["GET","POST"])
def user_delete(id):
    user=db.get_or_404(User, id)

    if request.method=="POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))
    return render_template("user/delete.html", user=user)
    
if __name__ == "__main__":
   
    app.run(debug=True)
