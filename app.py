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
from QLearning import QLearning
import numpy as np
import datetime
import os
import math
import random
import time


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
    return render_template("user/application.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            error_message = "ユーザー名またはパスワードが間違っています。"
            return render_template('user/login.html', error=error_message)
    return render_template('user/login.html')
        
@app.route("/tweets")
def tweets():
    return render_template("main/tweets.html")


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

@app.route("/user/<int:id>/delete",methods=["GET","POST"])
def user_delete(id):
    user=db.get_or_404(User, id)

    if request.method=="POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))
    return render_template("user/delete.html", user=user)

@app.route("/index", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['selected_set'] = request.form['select_set']
        session['incorrect_mode'] = False
        return redirect(url_for('quiz'))
    return render_template("main/index.html")

def get_questions_by_set(select_set):
    return [q for q in questions if q['select_set'] ==  select_set]

num_questions = len(questions)
q1 = QLearning(num_questions)

def select_question():
    if 'solved_questions' not in session:
        session['solved_questions'] = []     
        
    if 'incorrect_questions' not in session:
        session['incorrect_questions'] = []

    selected_set = session.get('selected_set', None)
    if not selected_set:
        return redirect(url_for('index'))
    
    available_questions = get_questions_by_set(selected_set)
    total_questions = len(available_questions)

    if session.get('incorrect_mode', False):
        unanswered_questions = [q['id'] for q in available_questions if q['id'] in session['incorrect_questions'] and q['id'] not in session['solved_questions']]
    else:
        unanswered_questions = [q['id'] for q in available_questions if q['id'] not in session['solved_questions']]

    return random.choice(unanswered_questions) if unanswered_questions else None
              
@app.route('/quiz',methods=['GET'])
def quiz():
    if 'selected_set' not in session:
        return redirect(url_for('index'))  # 問題セットが未選択ならトップへ戻す

    selected_set = session['selected_set']
    available_questions = get_questions_by_set(selected_set)

    if 'current_question' not in session:
        selected_question = select_question()
        
        if selected_question is None:  # すべて解かれている場合
            return redirect(url_for('result')) 
        
        session['current_question'] = selected_question
        session['solved_questions'] = []
        session['correct_answers'] = 0
        session['incorrect_questions'] = []
        session['progress'] = []
        session['start_time'] = time.time()
        session['incorrect_mode'] = False

    current_question_index = int(session['current_question'])
    current_question = questions[current_question_index]

    if session['current_question'] is None:
        return redirect(url_for('result'))  

    if session.get('incorrect_mode', False):
        unanswered_questions = [q for q in session['incorrect_questions'] if q not in session['solved_questions']]
        if unanswered_questions:
            session['current_question'] = unanswered_questions[0]
        else:
            return redirect(url_for('result'))

    # 'question_0'の問題がすべて解かれたかを確認
    question_0_questions = [q for q in questions if q['select_set'] == 'question_0']
    solved_question_indices = session.get('solved_questions', [])

    # 'question_0'のすべての問題が解かれたらresultページにリダイレクト
    if len(solved_question_indices) == len(question_0_questions):
        session['solved_questions'] = []
        return redirect(url_for('result')) 

    question_1_questions = [q for q in questions if q['select_set'] == 'question_1']
    solved_question_indices_1 = [q['id'] for q in question_1_questions if q['id'] in session.get('solved_questions', [])]

    # 'question_1'のすべての問題が解かれたらresultページにリダイレクト
    if len(solved_question_indices_1) == len(question_1_questions):
        return redirect(url_for('result')) 
    
    return render_template('main/quiz.html', question = current_question)

@app.route('/review', methods=['POST'])
def review():

    selected_answer = request.form.get('answer')
    current_question_index = int(session['current_question'])
    current_question = questions[current_question_index]
    correct_answer = current_question["answer"]

    start_time = session.get('start_time', time.time())
    time_spent = round(time.time() - start_time, 2)
    session['start_time'] = time.time()

    # 正解の場合と不正解の場合の処理
    if selected_answer == correct_answer:
        feedback = "正解です！！"
        reward = -1
        if not session.get('incorrect_mode', False):
            session['correct_answers'] = session.get('correct_answers', 0) + 1
    else:
        feedback = "不正解です!!"
        reward = 1
        if current_question_index not in session['incorrect_questions']:
            session['incorrect_questions'].append(current_question_index)

    #進捗データの記録
    session.setdefault('progress', [])
    session['progress'].append({
        'question_id': current_question_index,
        'selected_answer':selected_answer,
        'correct': selected_answer == correct_answer,
        'time_spent': time_spent,
        'section': current_question['select_set']
    })

    # 次の問題を選択
    next_question = select_question()
    if next_question is not None:
        q1.update_q_value(current_question_index, reward, next_question)
        session['current_question'] = next_question
    else:
        return redirect(url_for('result'))
    # 解答済み問題リストに現在の問題を追加
    if current_question_index not in session['solved_questions']:
        session['solved_questions'].append(current_question_index)

    # 解答済みと正解数を元に正答率を計算
    total_solved = len(session['solved_questions'])
    correct_answers = session.get('correct_answers', 0)

    # ゼロ除算を避けるため、total_solved > 0 のときだけ計算
    if total_solved > 0:
        accuracy = round(correct_answers / total_solved * 100, 1)
    else:
        accuracy = 0  # 解答がない場合は0%

    section_accuracy = {}
    section_counts = {}

    for progress in session['progress']:
        section = progress['section']
        if section not in section_accuracy:
            section_accuracy[section] = 0
            section_counts[section] = 0
        if progress['correct']:
            section_accuracy[section] += 1
        section_counts[section] += 1

    for section in section_accuracy:
        section_accuracy[section] = round((section_accuracy[section] / section_counts[section]) * 100, 1)

    session.modified = True

    return render_template('main/review.html', question=current_question, feedback=feedback, 
                           explanation=current_question["explanation"], solved_count=len(session['solved_questions']),
                           total_questions=len(questions), accuracy=accuracy,section_accuracy=section_accuracy)


@app.route('/next_question', methods=['POST'])
def next_question():
    session['current_question'] = int(select_question())
    return redirect(url_for('quiz'))

@app.route('/result', methods=['GET'])
def result():
    solved_question_indices = session.get('solved_questions', [])
    correct_answers = session.get('correct_answers', 0)

    question_0_questions = [q for q in questions if q['select_set'] == 'question_0']
    total_questions = len(question_0_questions)

    if total_questions > 0:
        accuracy = round((correct_answers / total_questions) * 100, 1)
    else:
        accuracy = 0

    incorrect_questions = session.get('incorrect_questions', [])
    incorrect_questions_details = [questions[i] for i in incorrect_questions]

    return render_template('main/result.html', total_questions = total_questions, correct_answers = correct_answers, accuracy = accuracy,incorrect_questions_details = incorrect_questions_details)

@app.route('/incorrect_mode',methods=['POST'])
def incorrect_mode():
    session['incorrect_mode'] = True
    session['solved_questions'] = []
    session['current_question'] = session['incorrect_questions'][0]
    return redirect(url_for('quiz'))

if __name__ == "__main__":
   
    app.run(debug=True)
