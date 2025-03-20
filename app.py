# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import LoginManager, UserMixin, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from transformers import pipeline
from questions import questions
from QLearning import QLearning
from flask_login import logout_user
import speech_recognition as sr
import numpy as np
import requests
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
    correct_count: Mapped[int] = mapped_column(Integer, default=0)  # 正解数
    total_count: Mapped[int] = mapped_column(Integer, default=0)    # 解いた問題数
    avg_time: Mapped[float] = mapped_column(db.Float, default=0.0) # 平均回答時間（秒）

    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")


    user=relationship("User", back_populates="progress")
    topic=relationship("Topic", back_populates="progress")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#User一覧の表示
@app.route("/")
def main():
    return render_template("user/application.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

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

    if session.get('incorrect_mode', False):
        unanswered_questions = [i for i in session['incorrect_questions'] if i not in session['solved_questions']]
    else:
        unanswered_questions = list(range(len(questions)))

    if unanswered_questions:
        next_question = random.choice(unanswered_questions)
    else:
        next_question = random.choice(range(len(questions)))
    
    if not session.get('incorrect_mode', False):
        next_question = next_question = q1.select_action()

    return next_question
              
@app.route('/quiz',methods=['GET'])
def quiz():
    if 'current_question' not in session:
        session['current_question'] = int(select_question())

    current_question_index = int(session['current_question'])
    current_question = questions[current_question_index]

    return render_template('main/quiz.html', question = current_question)

@app.route('/review', methods=['POST'])
def review():

    selected_answer = request.form.get('answer')
    current_question_index = int(session['current_question'])
    current_question = questions[current_question_index]
    correct_answer = current_question["answer"]

    if selected_answer == correct_answer:
        feedback = "正解です！！"
        reward = -1
        session['correct_answers'] = session.get('correct_answers', 0) + 1
    else:
        feedback = "不正解です!!"
        reward = 1
        if current_question_index not in session['incorrect_questions']:
            session['incorrect_questions'].append(current_question_index)

    next_question = int(select_question())
    q1.update_q_value(current_question_index, reward, next_question)
    session['current_question'] = next_question

    if 'current_question_index' not in session['solved_questions']:
        session['solved_questions'].append(current_question_index)

    total_solved = len(session['solved_questions'])
    correct_answers = session.get('correct_answers', 0)
    accuracy = round(correct_answers / total_solved * 100, 1) if total_solved > 0 else 0

    session.modified = True

    return render_template('main/review.html', question = current_question, feedback=feedback, explanation = current_question["explanation"],solved_count  = len(session['solved_questions']),total_questions = len(questions),accuracy=accuracy)


@app.route('/next_question', methods=['POST'])
def next_question():
    session['current_question'] = int(select_question())
    return redirect(url_for('quiz'))

@app.route('/incorrect_mode', methods=['POST'])
def incorrect_mode():
    session['incorrect_mode'] = True
    session['solved_questions'] = []  # 既に解いた問題をリセット
    if 'incorrect_questions' not in session:
        session['incorrect_questions'] = []
    return redirect(url_for('quiz'))

@app.route('/all_mode', methods=['POST'])
def all_mode():
    session['incorrect_mode'] = False
    session['solved_questions'] = []
    session['incorrect_questions'] = []  # 間違えた問題リストもリセット
    return redirect(url_for('quiz'))

#進捗の可視化
@app.route("/progress")
def progress():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    progress_data = db.session.query(
        LearningProgress.topic_id, 
        db.func.sum(LearningProgress.correct_count),
        db.func.sum(LearningProgress.total_count)
    ).filter_by(user_id=current_user.id).group_by(LearningProgress.topic_id).all()

    topic_names = []
    accuracy = []

    for topic_id, correct, total in progress_data:
        topic = Topic.query.get(topic_id)
        topic_names.append(topic.name)
        accuracy.append(round(correct / total * 100, 1) if total > 0 else 0)

    return render_template("main/progress.html", labels=topic_names, data=accuracy)

#音声認識機能
recognizer = sr.Recognizer()

def listen_to_audio():
    with sr.Microphone() as source:
        print("聞いています...")
        audio = recognizer.listen(source)
    try:
        print("認識したテキスト: " + recognizer.recognize_google(audio, language="ja-JP"))
        return recognizer.recognize_google(audio, language="ja-JP")
    except sr.UnknownValueError:
        return "聞き取れませんでした"
    except sr.RequestError as e:
        return "音声認識サービスに接続できませんでした"

# チャットボット
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium")

# Wikipedia APIを利用して情報を取得
def get_wikipedia_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("extract", "情報を取得できませんでした。")
    except requests.exceptions.RequestException as e:
        return "Wikipedia APIの取得に失敗しました。"

# チャット処理
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    if request.method == "POST":
        user_message = request.json.get("message")

        # 音声入力を処理する場合
        if user_message == "音声で入力":
            user_message = listen_to_audio()  # 音声認識

        # Wikipedia APIを利用
        if "とは" in user_message:
            query = user_message.replace("とは", "").strip()
            bot_response = get_wikipedia_summary(query)
        else:
            # 会話履歴をモデルの入力として渡す
            conversation_history = " ".join([msg['text'] for msg in session['chat_messages']])
            input_text = conversation_history + " " + user_message
            bot_response = chatbot(input_text, max_length=100, pad_token_id=50256, temperature=0.7, top_p=0.9)[0]['generated_text']

        # 会話履歴を追加
        session['chat_messages'].append({"sender": "あなた", "text": user_message})
        session['chat_messages'].append({"sender": "Bot", "text": bot_response})

        # 履歴を制限する（最大10件）
        MAX_HISTORY = 10
        if len(session['chat_messages']) > MAX_HISTORY:
            session['chat_messages'] = session['chat_messages'][-MAX_HISTORY:]

        return jsonify({"response": bot_response})

    return render_template("main/chat.html", chat_messages=session['chat_messages'])

if __name__ == "__main__":
    app.run(debug=True)