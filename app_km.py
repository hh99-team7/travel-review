from flask import Flask, render_template,request
import requests
from bs4 import BeautifulSoup
import certifi
from flask_sqlalchemy import SQLAlchemy
import os


# db 연결
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    

    def __repr__(self):
        return f'{self.title}>'

with app.app_context():
    db.create_all()


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


if __name__ == '__main__':
    app.run(debug=True)
