import csv
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productspy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    sku = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    name = db.Column(db.String(50), unique=True)
    brand = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<users {self.sku}>"


@app.route("/")
def index():
    info = []
    try:
        info = Product.query.all()
    except:
        print("Ошибка чтения из БД")
    return render_template("index.html", title="Главная", list=info)


@app.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "POST":
        try:

            p = Product(sku=request.form['sku'], price=request.form['price'], quantity=request.form['quantity'],
                        name=request.form['name'], brand=request.form['brand'])
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('index'))

    return render_template("register.html", title="Регистрация")


@app.route("/delete", methods=("POST", "GET"))
def delete():
    if request.method == "POST":
        try:
            Product.query.filter_by(sku=request.form['sku']).delete()
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('index'))

    return render_template("delete.html", title="Удаление")


# не нашел способа выдергивать файл из кэша. сохраняю в корень диска оттуда и тяну обратно.
app.config["IMAGE_UPLOADS"] = 'C:/'


@app.route("/uploadfile", methods=["GET", "POST"])
def uploadfile():
    if request.method == "POST":
        try:
            if request.files:
                image = request.files["image"]
                filename = secure_filename(image.filename)

                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                print(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                # print(image)

                with open(os.path.join(app.config["IMAGE_UPLOADS"], filename), newline='') as f:
                    reader = csv.reader(f)
                    data = list(reader)

                # print(data)SKU  PRICE   NAME  QUANTITY   BRAND  SIZE   COLOR
                for item in data:
                    item = item[0]
                    item = item.split(';')
                    print(item)
                    print(item[0])
                    print(item[1])
                    print(item[2])
                    print(item[3])
                    print(item[4])

                    p = Product(sku=item[0], price=item[1], name=item[2], quantity=item[3], brand=item[4])
                    # print("prod = ", p)
                    db.session.add(p)
                    # db.session.update(p)
                    db.session.commit()
                # f = OpenExcel(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                # f.read()  # read all
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
    return render_template("uploadfile.html", title="Добавление")


if __name__ == "__main__":
    app.run(debug=True)
