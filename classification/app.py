import base64
import io
import os
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image,ImageDraw,ImageFont

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        #后端接受前端数据
        avatar = request.files.get('avatar')  # 获取文件：request.files
        basepath = os.path.dirname(__file__)
        picname = secure_filename(avatar.filename)  # 防黑客在文件名上做手脚：../../User/xxx/.bashrc
        upload_path = os.path.join(basepath, 'images', picname)
        avatar.save(upload_path)  # 保存文件

        #上传原图片img1
        figfile1 = io.BytesIO(open(upload_path, 'rb').read())
        img1 = base64.b64encode(figfile1.getvalue()).decode('ascii')
        # return render_template('upload_ok.html', img1=img1)

        host = "https://southcentralus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/ed072838-ba30-4be9-aff3-3c160379820d/classify/iterations/Iteration1/image"
        with open(upload_path,"rb") as f:
            pic_datab=f.read()

        try:
            headers = {
                "Prediction-Key": "ff5bbe36d65b429e88a9c0d9d60aa044",
                "Content-Type": "application/octet-stream"
            }
            data=pic_datab
            response = requests.post(host,headers=headers, data=data)

            response.raise_for_status()  # 如果状态不是200，引发HTTPError异常
            response_json=response.json()

            predictions=response_json.get("predictions")

            sorted_predictions=sorted(predictions, key=lambda keys: keys['probability'],reverse=True)


            result=sorted_predictions[0]
            result_tagname=result['tagName']

            base = Image.open(upload_path).convert("RGBA")
            draw = ImageDraw.Draw(base)
            text=result_tagname
            imgfont = ImageFont.truetype("arial.ttf", size=60)
            draw.text((350,300), text, fill=(255, 0, 0),font=imgfont)

            processed_path = os.path.join(basepath, 'processedimage', picname)
            # print(processed_path)
            base.save(processed_path,"png")
            base.close()
            #上传处理图片img2
            figfile2 = io.BytesIO(open(processed_path, 'rb').read())
            img2 = base64.b64encode(figfile2.getvalue()).decode('ascii')
            return render_template('upload_ok.html',img2=img2)
        except:
             return jsonify(msg="wrong")
    #后端向前端递交
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)