from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///radio.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

# Create uploads directory if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    filename = db.Column(db.String(100))

@app.route('/')
def home():
    songs = Song.query.all()
    return render_template('index.html', songs=songs)

@app.route('/stream')
def stream():
    def generate():
        songs = Song.query.all()
        while True:
            for song in songs:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], song.filename)
                with open(filepath, 'rb') as f:
                    data = f.read(1024 * 1024)  # Read 1MB chunks
                    while data:
                        yield data
                        data = f.read(1024 * 1024)
    return Response(generate(), mimetype='audio/mpeg')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        file = request.files['file']
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_song = Song(title=title, artist=artist, filename=filename)
            db.session.add(new_song)
            db.session.commit()
            
            return redirect(url_for('home'))
    
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)