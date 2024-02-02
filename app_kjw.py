import json
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request, url_for
import os
from flask_sqlalchemy import SQLAlchemy
import requests
import urllib.request

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Review(db.Model):
    """ 리뷰 테스트옹 DTO"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    tour_id = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.tour_id} 내용 {self.content}'


class User(db.Model):
    """ 유저 테스트용 DTO"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'{self.user_id} '


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    """ 상세 페이지 리다이렉트"""
    return redirect(url_for('review'))


@app.route("/review")
def review():
    """ 상세 페이지 연결"""
    context = {
        'is_login': True,
        'review': Review.query.filter_by(user_id='user_id', tour_id='tour_id').all(),
    }
    return render_template('detail2.html', data=context)


@app.route("/review/create/", methods=['POST'])
def review_create():
    """ 리뷰 저장 데모코드"""
    context = {
        'is_login': True,
        'review': [],
    }
    user_id_res = request.form['user_id']
    tour_id_res = request.form['tour_id']
    content_res = request.form['content']
    img_url_res = request.form['img_url']
    point_res = request.form['point']

    review = Review(user_id=user_id_res,
                    tour_id=tour_id_res, content=content_res)
    db.session.add(review)
    db.session.commit()

    return redirect(url_for('review', data=context))


if __name__ == "__main__":
    app.run(debug=True)
