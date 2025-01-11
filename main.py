import os
import base64
import random
import webview
from tkinter import filedialog
from PIL import Image
from keras.models import load_model
import tensorflow as tf
import pandas as pd
from datetime import datetime
import cv2
import numpy as np

html = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Solar Panel Hotspot Detector</title>
    <style>
        body {
            text-align: center;
        }

        #title {
            font-size: 24px;
            margin-top: 20px;
        }

        #buttons {
            margin-top: 20px;
        }

        button {
            font-size: 16px;
            padding: 10px 20px;
            margin: 0 10px;
        }

        #images {
            margin-top: 20px;
        }

        img {
            max-width: 150px;
            max-height: 150px;
            margin: 0 10px;
        }

        #analyse-button {
            margin-top: 20px;
        }

         #saveButton {
            margin-top: 20px;
        }

        table {
            margin-top: 20px;
            border-collapse: collapse;
            margin-left: auto;
            margin-right: auto;
        }

        th,
        td {
            border: 1px solid black;
            padding: 5px 10px;
        }
    </style>
    <script>
        function analyseFolder() {
            pywebview.api.analyseFolder().then(function (response) {
                displayImages(response);
            });
        }

        function analyseImage() {
            pywebview.api.analyseImage().then(function (response) {
                displayImages(response);
            });
        }

        function displayImages(images) {
            var imagesDiv = document.getElementById('images');
            imagesDiv.innerHTML = '';
            for (var i = 0; i < 5; i++) {
                var img = document.createElement('img');
                img.src = 'data:image/png;base64,' + images[i];
                imagesDiv.appendChild(img);
            }
        }

        function analyseImages() {
            pywebview.api.analyseImages().then(function (response) {
                var table = '<table><tr><th>Image File Name</th><th>Image Resolution</th><th>Class</th></tr>';
                for (var i = 0; i < response.length; i++) {
                    table += '<tr><td>' + response[i][0] + '</td><td>' + response[i][1] + '</td><td>' + response[i][2] + '</td></tr>';
                }
                table += '</table>';
                var analysisDiv = document.getElementById('analysis');
                analysisDiv.innerHTML = table;
                var saveButtonDiv = document.getElementById('saveButton');
                saveButtonDiv.innerHTML = '<button onclick="saveResult()">Save Result</button>';
            });
        }

        function saveResult() {
            pywebview.api.saveResult().then(function (response) {
                var saveButtonDiv = document.getElementById('saveButton');
                saveButtonDiv.innerHTML = '<h3>'+response+'</h3>';
            });
        }
    </script>
</head>

<body>
    <div id="title">Solar Panel Hotspot Detector</div>
    <div id="buttons">
        <button onclick="analyseFolder()">Analyse Folder</button>
        <button onclick="analyseImage()">Analyse Image</button>
    </div>
    <div id="images"></div>
    <div id="analyse-button">
        <button onclick="analyseImages()">Generate Results</button>
    </div>
    <div id="analysis"></div>
    <div id="saveButton"></div>
</body>

</html>
"""

class Api:
    def __init__(self):
        self.images = []
        self.results = []

    def analyseFolder(self):
        print('analyseFolder called')
        folder_path = filedialog.askdirectory()
        if folder_path:
            image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpeg', '.png', '.jpg', '.JPG', '.JPEG', '.PNG'))]
            self.images = image_files
            return [self.encode_image(image) for image in self.images]
        return []

    def analyseImage(self):
        print('analyseImage called')
        file_path = filedialog.askopenfilename(filetypes=[('Image Files', '*.jpeg;*.png;*.jpg;*.JPG;*.JPEG;*.PNG')])
        if file_path:
            self.images = [file_path]
            return [self.encode_image(file_path)]
        return []

    def encode_image(self, image_path):
        print(f'encode_image called with {image_path}')
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

    def analyseImages(self):
        print('analyseImages called')
        print('Loading model...')
        model = load_model(r"C:\Users\naman\Downloads\test_RESNET50v2_blue.h5")
        print('Model Loaded.')
        result = []
        classes = ["Diode Failure","Dust/Shadow","Multi-Cell","PID Issue","Single-Cell"]
        for image in self.images:
            img = cv2.imread(image)
            height,width,_ = img.shape
            img=cv2.resize(img,(224,224))
            img_array = np.array([img/255.])
            pred = np.argmax(model.predict(img_array)) 
            result.append([os.path.basename(image), f'{width} x {height}', classes[pred]])
            print(f'Image {image} has resolution {width} x {height}')

        self.results=result
        return result

    def saveResult(self):
        print("Save Result Called")
        df = pd.DataFrame(self.results,columns=['FileName','Resolution','Class'])
        filename = 'results_'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
        df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),filename),index=False)
        return "File Saved."

if __name__ == '__main__':
    api = Api()
    window = webview.create_window('Solar Panel Hotspot Detector', html=html, js_api=api)
    webview.start(private_mode=True, storage_path=r"C:\Users\naman\Downloads")