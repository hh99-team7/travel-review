from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_required, LoginManager, login_manager
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'<users {self.username}>'

class review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tour_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<review {self.user_id}>'

def check_duplicate(username, email):
    #아이디,이메일 중복체크
    existing_username = users.query.filter_by(username=username).first()
    existing_email = users.query.filter_by(email=email).first()
    if existing_username:
        return 'username'
    elif existing_email:
        return 'email'
    else:
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # POST 요청일 때 로그인 시도
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("Received username:", username)
        print("Received password:", password)
        
        # 데이터베이스에서 사용자 확인
        user = users.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username  # 로그인 성공 시 세션에 사용자 이름 저장
            return render_template('index.html', success_message=f"{username}님 안녕하세요!")
            
        else:
            # 로그인 실패 알림창
            return render_template('login.html', failure_message='로그인 실패! 사용자 이름 또는 비밀번호가 잘못되었습니다.')
    
    # GET 요청일 때 로그인 페이지 표시
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # 세션에서 사용자 이름 제거
    return redirect('/')

@app.route('/')
def index():
    if 'username' in session: # 세션에 username이 있으면 값을 반환
        return render_template('index.html', username=session['username'])
    else:
        return render_template('index.html',logout_message="로그아웃!")

@app.route('/users/signup', methods=['GET', 'POST'])
def userRegister():
    #회원가입
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        # 비밀번호 확인
        if password != confirm_password:
            return render_template('signup.html', message='password_mismatch')

        duplicate = check_duplicate(username, email)
        if duplicate == 'username':
            return render_template('signup.html', message='username')
        elif duplicate == 'email':
            return render_template('signup.html', message='email')
        else:
            new_user = users(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            print(f'회원가입 성공: username={username}, email={email}')
            return render_template('home.html')

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)



