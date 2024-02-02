# Contain Flask application
from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import current_user, login_required, LoginManager, login_manager, UserMixin, login_user
import secrets

import os
import requests
from flask_sqlalchemy import SQLAlchemy
import certifi
from bs4 import BeautifulSoup


################################# 사전 정의 및 초기화 #######################################

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')


db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

################################# DTO 설정 ##################################################

# 유저 db 모델


class users(db.Model, UserMixin):
    """ User DTO """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'<users {self.username}>'


# 리뷰 db 모델
class Review(db.Model):
    """ Review DTO """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tour_id = db.Column(db.Integer, nullable=False)

    username = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)

    users = db.relationship('users', backref='reviews')

    def __repr__(self):
        return f'id: {self.id}, 작성자: {self.username}, 제목: {self.title}, 내용: {self.content},'


# 여행지 db 모델
class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)

    def __repr__(self):
        return f'{self.title}>'


with app.app_context():
    db.create_all()

################################# Home 관련 ##################################################

# @app.route('/seoul-viewer/<default_list>')
# @app.route('/')
# def home():
#     """ homepage main """
#     # return render_template('home.html', data = default_list)
#     return redirect(url_for('home_index'))


def get_tour_data():
    url = "https://apis.data.go.kr/B551011/KorService1/areaBasedList1?serviceKey=LsnvZ6LbK7IaMZ34Ob%2Fa9UpLifnuczwa7gMEfWZDbr3MsnFM5gAZuCcacAhQzr7ggfxiq1o34hkIVZ6HSuVGIQ%3D%3D&numOfRows=50&pageNo=1&MobileOS=ETC&MobileApp=AppTest&_type=json&listYN=Y&arrange=Q&contentTypeId=12&areaCode=1"
    response = requests.get(url, verify=certifi.where())
    data = response.json()
    print("API Response:", data)  # Debugging line
    return data['response']['body']['items']['item']

# db 에 저장


def save_to_db(tour_data):
    for item in tour_data:
        print(item)
        existing_tour = Tour.query.filter_by(title=item['title']).first()
        if not existing_tour:
            new_tour = Tour(
                title=item['title'],
                location=item['addr1'],
                content_id=item['contentid'],
                image_url=item.get('firstimage', '')  # 이미지 URL 추가
            )
            db.session.add(new_tour)
    db.session.commit()


# 서버가 켜지면 루트에 api 데이터 50개 저장
@app.route('/home')
def home_index():
    # if not current_user.is_authenticated:
    #     # Store the intended URL to redirect back after login
    #     return redirect(url_for('login'))
    tour_data = get_tour_data()
    save_to_db(tour_data[:50])  # 50개만 저장
    saved_tours = Tour.query.all()

    return render_template('home.html', data=saved_tours)


################################# User 관련 ##################################################

# 아이디,이메일 중복체크
def check_duplicate(username, email):
    existing_username = users.query.filter_by(username=username).first()
    existing_email = users.query.filter_by(email=email).first()
    if existing_username:
        return 'username'
    elif existing_email:
        return 'email'
    else:
        return None

# #메인 화면
# @app.route('/')
# def main():
#     return redirect(url_for('home_index'))


# 로그인 화면
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 데이터베이스에서 사용자 확인
        user = users.query.filter_by(
            username=username, password=password).first()
        if user:
            if user:
                login_user(user)
                session['username'] = username  # 로그인 성공 시 세션에 사용자 이름 저장
                return redirect(url_for('home_index'))

        else:
            # Stay on the login page with an error message
            return render_template('login.html', failure_message='로그인 실패! 사용자 이름 또는 비밀번호가 잘못되었습니다.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # 세션에서 사용자 이름 제거
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'username' in session:  # 세션에 username이 있으면 값을 반환
        # return render_template('home.html', username=session['username'])
        return redirect(url_for('home_index'))

    else:
        # return render_template('login.html',logout_message="로그아웃!")
        return redirect(url_for('login'))


@app.route('/users/signup', methods=['GET', 'POST'])
def userRegister():
    """ 회원 가입 이상이 없으면 DB에 저장"""
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
            login_user(new_user)

            return redirect(url_for('home_index'))

    return render_template('signup.html')


@app.route('/myreview')
def my_review():
    # 마이 리뷰 페이지x
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template('review_list.html', reviews=reviews)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = request.form.get('user_id')  # 수정
    username = request.form.get('username')
    email = request.form.get('email')
    user = users.query.get(user_id)
    if user:
        user.username = username
        user.email = email
        db.session.commit()
        return redirect(url_for('my_review'))  # 프로필 페이지 또는 다른 페이지로 리다이렉션
    else:
        return 'User not found', 404


@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = request.form.get('user_id')  # 수정
    user_id = int(user_id) if user_id.isdigit() else None  # user_id를 정수로 변환
    if user_id is not None:
        user = users.query.get(user_id)
        if user:
            # 사용자가 작성한 모든 리뷰를 찾아서 삭제
            reviews = Review.query.filter_by(user_id=user_id).all()
            for review in reviews:
                db.session.delete(review)

            # 사용자 계정 삭제
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return 'User not found', 404
    else:
        return 'Invalid user ID', 400


################################# 여행지 정보 관련 ##################################################

# tour.title 을 이용하여 관광지 검색
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_title = request.form['search_title']
        results = Tour.query.filter(Tour.title.contains(search_title)).all()
        return render_template('home.html', data=results)
    return render_template('home.html', data=[])


def get_tourist_place_details(content_id):
    # API service key
    service_key = "e1MMpT7St3EHSxcRRYM4EM%2BKpD%2BYa07ocfY%2BrKoJzauIJcoridA7C0dw2pacHyCGWAZ6NtZeFMNsGpY5fHYusw%3D%3D"
    URL = f"http://apis.data.go.kr/B551011/KorService1/detailCommon1?ServiceKey={service_key}&contentId={content_id}&MobileOS=ETC&MobileApp=SeoulViewer&defaultYN=Y&firstImageYN=Y&areacodeYN=Y&catcodeYN=Y&addrinfoYN=Y&mapinfoYN=Y&overviewYN=Y&_type=json"

    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# id별로 다른 컨텐츠 가져오기


@app.route('/details/<int:content_id>')
def show_place_details(content_id):
    # if not current_user.is_authenticated:
    #     # Store the intended URL to redirect back after login
    #     next_url = url_for('show_place_details', content_id=content_id)
    #     return redirect(url_for('login', next=next_url))

    json_data = get_tourist_place_details(content_id)

    if json_data:
        reviews = Review.query.filter_by(tour_id=content_id).all()

        context = {
            'is_login': True,
            'review': reviews,
        }
        item = json_data.get('response', {}).get(
            'body', {}).get('items', {}).get('item', [])[0]
        return render_template('detail.html', place=item, user_id=current_user.id, data=context, content_id=content_id, context=context)
    else:
        return "Details not found", 404

################################# 리뷰 관련 ##################################################

# 리뷰 작성 화면
@app.route('/review/<int:content_id>')
def review(content_id):
    username = users.query.filter_by(id=current_user.id).first()
    return render_template('review_regist.html', content_id=content_id, username=username, user_id=current_user.id)


# @app.route('/review')
# def review():
#     return render_template('review_regist.html')


# 리뷰 등록
@app.route('/reviewRegister', methods=['GET', 'POST'])
def reviewRegister():
    # form으로 데이터 입력 받기
    username_receive = request.form.get("username")
    user_id_receive = request.form.get("user_id")
    tour_id_receive = request.form.get("content_id")
    title_receive = request.form.get("title")
    content_receive = request.form.get("content")
    image_receive = request.form.get("image_url")

    # 데이터를 DB에 저장하기
    review = Review(user_id=user_id_receive, tour_id=tour_id_receive, username=username_receive, title=title_receive,
                    content=content_receive, image_url=image_receive)
    db.session.add(review)
    db.session.commit()

    return redirect(url_for('show_place_details', content_id=tour_id_receive))


# 리뷰 전체 보기
@app.route('/review/list')
def reviewList():
    reviews = Review.query.all()
    print(reviews)
    return render_template('review_list.html', reviews=reviews)

# 리뷰 업데이트 라우트


@app.route('/reviewUpdate')
def reviewUpdate():
    review_data = Review.query.filter_by(user_id=request.args.get("id")).first()
    
    # 폼 데이터 가져오기
    username = request.args.get("username")
    review_data.username = username
    review_data.user_id = request.args.get("user_id")
    review_data.tour_id = request.args.get("tour_id")
    review_data.title = request.args.get("title")
    review_data.content = request.args.get("content")
    review_data.image_url = request.args.get("image_url")

    # 데이터베이스에 업데이트 저장
    db.session.commit()
    return redirect(url_for('reviewList'))

# 리뷰 삭제 라우트
@app.route('/delete_review/<delete_id>')
def reviewDelete(delete_id):
    review = Review.query.get_or_404(delete_id)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('reviewList'))


if __name__ == '__main__':
    app.run(debug=True)
