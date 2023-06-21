from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash,
    jsonify,
    session
)
from flask import jsonify, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import hashlib
import jwt
import re
import random
from os.path import join, dirname
import datetime
from datetime import datetime,timedelta
import os
import base64
import certifi
ca = certifi.where()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
DB_COLLECTION = os.environ.get("DB_COLLECTION")
DB_USERS_COLLECTION = os.environ.get("DB_USERS_COLLECTION")
DB_COMMENT_COLLECTION = os.environ.get("DB_COMMENT_COLLECTION")


client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

collection = db[DB_COLLECTION]

users_collection = db[DB_USERS_COLLECTION]

comment_collection = db[DB_COMMENT_COLLECTION]


app = Flask(__name__)


SECRET_KEY = 'ANIMALS'


# app.secret_key = 'your_secret_key'

# dari hamdan
profile_pics_dir = 'static/profile_pics' 



@app.route('/')
def main():
    return render_template('home.html')

@app.route('/signup', methods=['GET'])
def signup():
    msg = request.args.get('msg')
    return render_template('signin.html')

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    confirm_password = request.form.get('confirm_password')
    
    
    existing_user = db.users.find_one({'$or': [{'fullname': fullname}, {'email': email}]})
    if existing_user: 
        return jsonify({'success': False, 'message': 'Nama atau email sudah terdaftar.'})

    profile_pic_filename = random.choice(os.listdir(profile_pics_dir))
    profile_pic_path = os.path.join(profile_pics_dir, profile_pic_filename)

    user = {
        'Nama Lengkap': fullname,
        'Email': email,
        'Password': password_hash,
        'Profile_Pic': profile_pic_path.replace('\\', '/')
    }

    db.users.insert_one(user)

    return jsonify({'success': True, 'message': 'Registrasi berhasil.', 'profile_pic': profile_pic_filename})

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in User
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "Email": email_receive,
            "Password": pw_hash,
        }
    )
    print(result)
    if result:
        payload = {
            "id": email_receive,
            # Code dibawah ini agar user cuma bisa login 24 jam
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Ketika user salah memasukkan akun maka akan terjadi hal berikut.
    else:
        return jsonify(
            {
                "result": "fail",
            }
        )

@app.route("/home2", methods=['GET'])
def home2():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})


    #nah, sekarang kita buat sebuah variabel 'animal' yang menampung isi dari data
    return render_template('home2.html', animal=data)


@app.route("/admin", methods=['GET'])
def admin():
    return render_template('admin.html')

@app.route("/signin-admin", methods=['POST'])
def signin_admin():
    # Sign in Admin
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.admin.find_one(
        {
            "Email": email_receive,
            "Password": pw_hash,
        }
    )
    print(result)
    if result:
        payload = {
            "id": email_receive,
            # Code dibawah ini agar admin cuma bisa login 24 jam
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Ketika admin salah memasukkan akun maka akan terjadi hal berikut.
    else:
        return jsonify(
            {
                "result": "fail",
            }
        )





# Route grup vertebrata

@app.route("/vertebrata", methods=['GET'])
def vertebrata():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('vertebrata.html', articles=results, rekomendasi=rekomendasi, animal=data)





@app.route("/pisces", methods=['GET'])
def pisces():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('pisces.html', articles=results, rekomendasi=rekomendasi, animal=data)





@app.route("/amfibi", methods=['GET'])
def amfibi():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('amfibi.html', articles=results, rekomendasi=rekomendasi, animal=data)



@app.route("/reptil", methods=['GET'])
def reptil():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}, 'kelas': 'reptilia'} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}, 'kelas': 'reptilia'})
        if result:
            results.append(result)

    return render_template('reptil.html', articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/aves", methods=['GET'])
def aves():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('aves.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/mammalia", methods=['GET'])
def mammalia():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('mammalia.html' , articles=results, rekomendasi=rekomendasi, animal=data)






# Route grup invertebrata

@app.route("/invertebrata", methods=['GET'])
def invertebrata():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('invertebrata.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/porifera", methods=['GET'])
def porifera():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('porifera.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/platyhelminthes", methods=['GET'])
def platyhelminthes():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('platyhelminthes.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/nemathelminthes", methods=['GET'])
def nemathelminthes():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('nemathelminthes.html' ,articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/coelenterata", methods=['GET'])
def coelenterata():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('coelenterata.html' ,articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/annelida", methods=['GET'])
def annelida():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('annelida.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/mollusca", methods=['GET'])
def mollusca():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('mollusca.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/echinodermata", methods=['GET'])
def echinodermata():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('echinodermata.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/arthropoda", methods=['GET'])
def arthropoda():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 3)
    data = db.users.find_one({'Email': email})

    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('arthropoda.html' , articles=results, rekomendasi=rekomendasi, animal=data)

@app.route("/aboutus", methods=["GET"])
def aboutus():
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload['id']

    data = db.users.find_one({'Email': email})

    return render_template('aboutus.html' , animal=data)









# Rute dari Stef

@app.template_filter('b64encode')
def base64_encode(data):
    encoded_data = base64.b64encode(data).decode('utf-8')
    return encoded_data



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        nama_hewan = request.form['Nama_Hewan']
        gambar1 = request.files['image1']
        sumber_foto1 = request.form['sumberfoto1']
        kerajaan = request.form['Kerajaan']
        filum = request.form['Filum']
        kelas = request.form['kelas']
        ordo = request.form['Ordo']
        famili = request.form['famili']
        genus = request.form['Genus']
        spesies = request.form['Spesies']
        deskripsi_fisik = request.form['Deskripsi_Fisik']
        habitat = request.form['Habitat']
        distribusi_geografis = request.form['Distribusi_Geografis']
        gambar2 = request.files['image2']
        sumber_foto2 = request.form['sumberfoto2']
        makanan = request.form['Makanan']
        kebiasaan_dan_perilaku = request.form['Kebiasaan_dan_Perilaku']
        reproduksi = request.form['Reproduksi']
        gambar3 = request.files['image3']
        sumber_foto3 = request.form['sumberfoto3']
        karakteristik_unik = request.form['Karakteristik_Unik']
        konservasi = request.form['Konservasi']
        fakta_menarik = request.form['Fakta_Menarik']
        header_referensi = request.form['HeaderReferensi']
        referensi_1 = request.form['Referensi_1']
        referensi_2 = request.form['Referensi_2']
        referensi_3 = request.form['Referensi_3']
        referensi_4 = request.form['Referensi_4']


        now = datetime.datetime.now()

        article = {
        'Nama_Hewan': nama_hewan,
        'image1': gambar1.filename,
        'sumberfoto1': sumber_foto1,
        'Kerajaan': kerajaan,
        'Filum': filum,
        'kelas': kelas,
        'Ordo': ordo,
        'famili': famili,
        'Genus': genus,
        'Spesies': spesies,
        'Deskripsi_Fisik': deskripsi_fisik,
        'Habitat': habitat,
        'Distribusi_Geografis': distribusi_geografis,
        'image2': gambar2.filename,
        'sumberfoto2': sumber_foto2,
        'Makanan': makanan,
        'Kebiasaan_dan_Perilaku': kebiasaan_dan_perilaku,
        'Reproduksi': reproduksi,
         'image3': gambar3.filename,
        'sumberfoto3': sumber_foto3,
        'Karakteristik_Unik': karakteristik_unik,
        'Konservasi': konservasi,
        'Fakta_Menarik': fakta_menarik,
        'HeaderReferensi': header_referensi,
        'Referensi_1': referensi_1,
        'Referensi_2': referensi_2,
        'Referensi_3': referensi_3,
        'Referensi_4': referensi_4,
        'datetime': now.strftime("%Y-%m-%d %H:%M:%S")

        }

       
        if gambar1:
            filename1 = secure_filename(f"{nama_hewan}1.{gambar1.filename.split('.')[-1]}")
            gambar1_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename1)
            gambar1.save(gambar1_path)
            article['image1'] = f'GambarArtikel/{filename1}'

        if gambar2:
            filename2 = secure_filename(f"{nama_hewan}2.{gambar2.filename.split('.')[-1]}")
            gambar2_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename2)
            gambar2.save(gambar2_path)
            article['image2'] = f'GambarArtikel/{filename2}'

        if gambar3:
            filename3 = secure_filename(f"{nama_hewan}3.{gambar3.filename.split('.')[-1]}")
            gambar3_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename3)
            gambar3.save(gambar3_path)
            article['image3'] = f'GambarArtikel/{filename3}'

        db.articles.insert_one(article)

        return 'Data berhasil diunggah ke MongoDB'

    return render_template('tulis_artikel.html')




@app.route('/Comment_admin')
def comment_admin():
    comments = db.comment.find()
    return render_template('comment_admin.html', comments=comments)


@app.route('/delete_comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        comment_id = ObjectId(comment_id)
        result = db.comment.delete_one({'_id': comment_id})
        if result.deleted_count > 0:
            return jsonify(success=True)
        else:
            return jsonify(success=False)
    except:
        return jsonify(success=False)

@app.route('/submit-comment', methods=['POST'])
def submit_comment():
    name = request.form.get('name')
    email = request.form.get('email')
    comment = request.form.get('comment')

    comment_data = {
        'name': name,
        'email': email,
        'comment': comment
    }
    db.comment.insert_one(comment_data)


    return 'Komentar berhasil dikirim!'



@app.route('/edit/<article_id>', methods=['GET'])
def edit_article(article_id):
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article is None:
        return 'Artikel tidak ditemukan'  # Ganti dengan penanganan error yang sesuai

    return render_template('Edit_Artikel.html', article=article)

@app.route('/update/<article_id>', methods=['POST'])
def update_article(article_id):
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article is None:
        return 'Artikel tidak ditemukan'  # Ganti dengan penanganan error yang sesuai

    # Dapatkan data dari formulir
    nama_hewan = request.form['Nama_Hewan']
    gambar1 = request.files['image1']
    sumber_foto1 = request.form['sumberfoto1']
    kerajaan = request.form['Kerajaan']
    filum = request.form['Filum']
    kelas = request.form['kelas']
    ordo = request.form['Ordo']
    famili = request.form['famili']
    genus = request.form['Genus']
    spesies = request.form['Spesies']
    deskripsi_fisik = request.form['Deskripsi_Fisik']
    habitat = request.form['Habitat']
    distribusi_geografis = request.form['Distribusi_Geografis']
    gambar2 = request.files['image2']
    sumber_foto2 = request.form['sumberfoto2']
    makanan = request.form['Makanan']
    kebiasaan_dan_perilaku = request.form['Kebiasaan_dan_Perilaku']
    reproduksi = request.form['Reproduksi']
    gambar3 = request.files['image3']
    sumber_foto3 = request.form['sumberfoto3']
    karakteristik_unik = request.form['Karakteristik_Unik']
    konservasi = request.form['Konservasi']
    fakta_menarik = request.form['Fakta_Menarik']
    header_referensi = request.form['HeaderReferensi']
    referensi_1 = request.form['Referensi_1']
    referensi_2 = request.form['Referensi_2']
    referensi_3 = request.form['Referensi_3']
    referensi_4 = request.form['Referensi_4']
    now = datetime.datetime.now()

    db.articles.update_one({'_id': ObjectId(article_id)}, {'$set': {
        'Nama_Hewan': nama_hewan,
        'sumberfoto1': sumber_foto1,
        'Kerajaan': kerajaan,
        'Filum': filum,
        'kelas': kelas,
        'Ordo': ordo,
        'famili': famili,
        'Genus': genus,
        'Spesies': spesies,
        'Deskripsi_Fisik': deskripsi_fisik,
        'Habitat': habitat,
        'Distribusi_Geografis': distribusi_geografis,
        'sumberfoto2': sumber_foto2,
        'Makanan': makanan,
        'Kebiasaan_dan_Perilaku': kebiasaan_dan_perilaku,
        'Reproduksi': reproduksi,
        'sumberfoto3': sumber_foto3,
        'Karakteristik_Unik': karakteristik_unik,
        'Konservasi': konservasi,
        'Fakta_Menarik': fakta_menarik,
        'HeaderReferensi': header_referensi,
        'Referensi_1': referensi_1,
        'Referensi_2': referensi_2,
        'Referensi_3': referensi_3,
        'Referensi_4': referensi_4,
        'datetime': now.strftime("%Y-%m-%d %H:%M:%S")
    }})

    if gambar1:
        filename1 = secure_filename(f"{nama_hewan}1.{gambar1.filename.split('.')[-1]}")
        gambar1_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename1)
        gambar1.save(gambar1_path)
        db.articles.update_one({'_id': ObjectId(article_id)}, {'$set': {'image1': f'GambarArtikel/{filename1}'}})


    if gambar2:
        filename2 = secure_filename(f"{nama_hewan}2.{gambar2.filename.split('.')[-1]}")
        gambar2_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename2)
        gambar2.save(gambar2_path)
        db.articles.update_one({'_id': ObjectId(article_id)}, {'$set': {'image2': f'GambarArtikel/{filename2}'}})

    if gambar3:
        filename3 = secure_filename(f"{nama_hewan}3.{gambar3.filename.split('.')[-1]}")
        gambar3_path = os.path.join(app.root_path, 'static', 'GambarArtikel', filename3)
        gambar3.save(gambar3_path)
        db.articles.update_one({'_id': ObjectId(article_id)}, {'$set': {'image3': f'GambarArtikel/{filename3}'}})
    
    return redirect(f'/edit/{article_id}')


@app.route('/Animal', methods=['GET'])
def template_artikel():
    query = request.args.get('query')
    results = []
    rekom = list(db.articles.find({}))
    rekomendasi = random.sample(rekom, 2)
    
    if query:
        keywords = query.split()
        regex_patterns = [{'Nama_Hewan': {'$regex': keyword, '$options': 'i'}} for keyword in keywords]
        search_query = {'$and': regex_patterns}
        results = list(db.articles.find(search_query).limit(1))

    if query and not results:
        result = db.articles.find_one({'Nama_Hewan': {'$regex': query, '$options': 'i'}})
        if result:
            results.append(result)

    return render_template('templateArtikel.html', articles=results, rekomendasi=rekomendasi)



@app.route('/delete_article/<article_id>', methods=['POST'])
def delete_article(article_id):
    try:
        result = collection.delete_one({'_id': ObjectId(article_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Artikel tidak ditemukan'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/')
def view():
    articles = db.articles.find()
    return render_template('view.html', articles=articles)

@app.route('/post')
def post():
    articles = db.articles.find()
    return render_template('post.html', articles=articles)



@app.route('/logout')
def logout():
    return render_template('logout.html')



@app.route('/cek')
def cek():
    articles = db.articles.find()

    return render_template('cek.html', articles=articles)



@app.route('/overview')
def overview():
    # Mengambil data dari rute Request
    requests = list(db.request.find())
    
    # Mengambil data dari rute post
    articles = list(db.articles.find())
    comments = list(db.comment.find())

    
    return render_template('overview.html', requests=requests, articles=articles, comments=comments)



@app.route('/Request')
def Request():
    requests = db.request.find()
    return render_template('Request.html', requests=requests)

@app.route('/approve', methods=['POST'])
def approve_request():
    request_id = request.json['requestId']
    db.request.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Disetujui'}})
    return jsonify({'success': True})
  


@app.route('/reject', methods=['POST'])
def reject_request():
    request_id = request.json['requestId']
    db.request.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Ditolak'}})
    return jsonify({'success': True})


@app.route('/deleteRequest', methods=['POST'])
def delete_request():
    request_id = request.json['requestId']
    db.request.delete_one({'_id': ObjectId(request_id)})
    return jsonify({'success': True})



@app.route('/help')
def help():
    requests = db.request.find()
    return render_template('templateRequestHelp.html')

@app.route('/submit-help', methods=['POST'])
def submit_help():
    name = request.form.get('name')
    email = request.form.get('email')
    article_title = request.form.get('article_title')
    message = request.form.get('message')
    status = 'Pending'
    if name and email and article_title and message:

        help = {
            'name': name,
            'email': email,
            'article_title': article_title,
            'message': message,
            'status': status
        }
        db.request.insert_one(help)

        return redirect(url_for('help', success='true'))
    else:
        return redirect(url_for('help'))


@app.route('/lonceng')
def home():
    return render_template('tesLonceng.html')

@app.route('/page-with-bell')
def page_with_bell():
    return render_template('page_with_bell.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            return redirect('/templateArtikel')
        else:
            flash('Email atau password salah', 'error')

    return render_template('login.html')


# @app.route('/register', methods=['POST'])
# def register():
#     fullname = request.form.get('fullname')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     confirm_password = request.form.get('confirm_password')

#     existing_user = db.users.find_one({'$or': [{'fullname': fullname}, {'email': email}]})
#     if existing_user:
        
#         return jsonify({'success': False, 'message': 'Nama atau email sudah terdaftar.'})
#     user = {
#         'fullname': fullname,
#         'email': email,
#         'password': password
#     }
#     db.users.insert_one(user)

#     return jsonify({'success': True, 'message': 'Registrasi berhasil.'})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
