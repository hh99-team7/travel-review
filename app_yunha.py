from flask import Flask, render_template, requests, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


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
    username_receive = requests.args.get("username")
    title_receive = requests.args.get("title")
    content_receive = requests.args.get("content")
    image_receive = requests.args.get("image_url")

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
    review_data.username = requests.form.get('username')
    print(requests.form.get('username'))
    review_data.title = requests.form.get('title')
    review_data.content = requests.form.get('content')
    review_data.image_url = requests.form.get('iamge_URL')

    db.session.add(review_data)
    db.session.commit()
    return redirect(url_for('reviewList'))


if __name__ == '__main__':
    app.run(debug=True)
