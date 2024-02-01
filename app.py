# Contain Flask application
from flask import Flask, render_template, redirect, url_for, request
import os
import requests
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import certifi


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

#윤하
# 여행지 db 모델
class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    

    def __repr__(self):
        return f'{self.title}>'

# 리뷰 데이터베이스 모델
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'id: {self.id}, 작성자: {self.username}, 제목: {self.title}, 내용: {self.content},'

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/review')
def review():
    return render_template('review_register.html')

@app.route('/reviewRegister')
def reviewRegister():
    # form으로 데이터 입력 받기
    username_receive = request.args.get("username")

    title_receive = request.args.get("title")
    content_receive = request.args.get("content")
    image_receive = request.args.get("image_url")

    # 데이터를 DB에 저장하기
    review = Review(username=username_receive, title=title_receive,
                    content=content_receive, image_url=image_receive)
    db.session.add(review)
    db.session.commit()

    return render_template('index.html')


@app.route('/review/list')
def reviewList():
    reviews = Review.query.all()
    print(reviews)
    return render_template('review_list.html', reviews=reviews)


@app.route('/review/<review_id>', methods=["POST"])
def reviewUpdate(review_id):
    print(review_id)
    review_data = Review.query.filter_by(id=review_id).first()
    # 폼 데이터 가져오기
    review_data.id = review_id
    review_data.username = request.form.get('username')
    print(request.form.get('username'))
    review_data.title = request.form.get('title')
    review_data.content = request.form.get('content')
    review_data.image_url = request.form.get('iamge_URL')

    db.session.add(review_data)
    db.session.commit()
    return redirect(url_for('reviewList'))

#경민
# api 를 가져옴
def get_tour_data():
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1?serviceKey=LsnvZ6LbK7IaMZ34Ob%2Fa9UpLifnuczwa7gMEfWZDbr3MsnFM5gAZuCcacAhQzr7ggfxiq1o34hkIVZ6HSuVGIQ%3D%3D&numOfRows=50&pageNo=1&MobileOS=ETC&MobileApp=AppTest&_type=json&areaCode=1"
    response = requests.get(url,verify=certifi.where())
    data = response.json()
    return data['response']['body']['items']['item']

# db 에 저장
def save_to_db(tour_data):
    for item in tour_data:
        existing_tour = Tour.query.filter_by(title=item['title']).first()
        if not existing_tour:
            new_tour = Tour(
                title=item['title'], 
                location=item['addr1'], 
                image_url=item.get('firstimage', '')  # 이미지 URL 추가
            )
            db.session.add(new_tour)
    db.session.commit()

# tour.title 을 이용하여 관광지 검색  
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_title = request.form['search_title']
        results = Tour.query.filter(Tour.title.contains(search_title)).all()
        return render_template('index.html', data=results)
    return render_template('index.html', data=[])


# 서버가 켜지면 루트에 api 데이터 50개 저장
@app.route('/')
def index():
    tour_data = get_tour_data()
    save_to_db(tour_data[:50])  #  50개만 저장
    saved_tours = Tour.query.all()

    return render_template('index.html', data=saved_tours)

#시현
# 외부API에서 여행지 가져오기
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
@app.route('/place/<int:content_id>')
def show_place_details(content_id=132215): 
    json_data = get_tourist_place_details(content_id)
    if json_data:
        item = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])[0]
        return render_template('detail.html', place=item)
    else:
        return "Details not found", 404
    

if __name__ == '__main__':
    app.run(debug=True)
