import base64
import io
import os
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import ImageFont,ImageDraw,Image

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

        host = "https://southeastasia.api.cognitive.microsoft.com/customvision/v3.0/Prediction/cdcbb1e1-967b-4f9f-b7d9-5fca97924bbb/detect/iterations/Iteration3/image"
        with open(upload_path,"rb") as f:
            pic_datab=f.read()

        try:
            headers = {
                "Prediction-Key": "167a6619fd6d428d9e9ff22ac4cd2ae0",
                "Content-Type": "application/octet-stream"
            }
            data=pic_datab
            response = requests.post(host,headers=headers, data=data)

            response.raise_for_status()  # 如果状态不是200，引发HTTPError异常
            response_json=response.json()
            predictions=response_json.get("predictions")

            sorted_predictions=sorted(predictions, key=lambda keys: keys['probability'],reverse=True)

            nresult = list(filter(lambda keys: keys['probability'] > 0.5, sorted_predictions))  # 使用匿名函数对列表data进行过滤

            im = Image.open(upload_path)
            base = Image.open(upload_path)
            for putout in nresult:
                # print(nresult)

                width_pix = im.size[0]
                height_pix= im.size[1]
                # print(width_pix)
                # print(height_pix)
                boundingbox=putout['boundingBox']
                # print(boundingbox)

                x0 = float(boundingbox['left'] * width_pix)
                y0 = float(boundingbox['top'] * height_pix)
                width=float(boundingbox['width']*width_pix)
                height=float(boundingbox['height']*height_pix)

                x2=x0+width
                y2=y0+height

                # print(x0)
                # print(y0)
                # print(width)
                # print(height)


                d = ImageDraw.Draw(base)
                d.rectangle([float(x0),float(y0),float(x2),float(y2)], outline='RED',width=3)
            processed_path = os.path.join(basepath, 'processedimage', picname)
            base.save(processed_path)
            base.close()


            # 上传处理图片img2
            figfile2 = io.BytesIO(open(processed_path, 'rb').read())
            img2 = base64.b64encode(figfile2.getvalue()).decode('ascii')
            return render_template('upload_ok.html', img1=img1,img2=img2,wid=width_pix,hei=height_pix)

        except:
             return jsonify(msg="wrong")
    #后端向前端递交
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)