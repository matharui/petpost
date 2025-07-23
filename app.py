from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

S3_BUCKET = 'petpost-images-inder'  # Replace with your actual S3 bucket name
S3_REGION = 'us-east-2'
PET_JSON = 'pets.json'

# Initialize S3 client
s3 = boto3.client('s3', region_name=S3_REGION)

@app.route('/')
def index():
    if os.path.exists(PET_JSON):
        with open(PET_JSON, 'r') as f:
            pets = json.load(f)
    else:
        pets = []
    return render_template('index.html', pets=pets)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        breed = request.form['breed']
        file = request.files['photo']
        filename = secure_filename(file.filename)

        # Upload image to S3
        s3.upload_fileobj(file, S3_BUCKET, filename)
        image_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

        # Save pet info to local JSON
        pet = {'name': name, 'age': age, 'breed': breed, 'image': image_url}
        pets = []
        if os.path.exists(PET_JSON):
            with open(PET_JSON, 'r') as f:
                pets = json.load(f)
        pets.append(pet)
        with open(PET_JSON, 'w') as f:
            json.dump(pets, f)
        return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
