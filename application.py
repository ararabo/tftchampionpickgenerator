from flask import Flask,render_template, request,url_for
import os
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
# import cv2
app = Flask(__name__)
# ---------------------------------------------------------------------
# 固定変数の設定
# ---------------------------------------------------------------------
# ディレクトリ
SAMPLE_IMAGE_NAME='sample_image.png'
IMAGES_DIR = './static/images'
FRAME_IMAGES_DIR='./static/frame_images'
ATTRIBUTE_IMAGES_DIR='./static/attribute_images/set4'
SPLASH_IMAGES_DIR='./static/splash_images'
UPLOAD_IMAGES_DIR='./static/upload_images'
# フォント設置
FONT_M_PATH ='./static/font/YuGothM.TTC'
FONT_B_PATH ='./static/font/YuGothB.TTC'
# ---------------------------------------------------------------------
# 画像のオーバーレイ
# ---------------------------------------------------------------------
def overlayimage(src, overlay, location):
    # 背景をPIL形式に変換
    # src = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
    pil_src = Image.fromarray(src)
    pil_src = pil_src.convert('RGBA')

    # オーバーレイをPIL形式に変換
    # overlay = cv2.cvtColor(overlay, cv2.COLOR_BGRA2RGBA)
    pil_overlay = Image.fromarray(overlay)
    pil_overlay = pil_overlay.convert('RGBA')

    # 画像を合成
    pil_tmp = Image.new('RGBA', pil_src.size, (255, 255, 255, 0))
    pil_tmp.paste(pil_overlay, location, pil_overlay)
    result_image = Image.alpha_composite(pil_src, pil_tmp)
    result_image_array=np.asarray(result_image)
    # OpenCV形式に変換
    return result_image_array

def imagemaker(name,tier,time_s,attribute1,attribute2,attribute1_icon,attribute2_icon,upfile,string_color,attribute_chosen):
    tier_name='tier'+str(tier)+'_frame.png'
    upfile.save(UPLOAD_IMAGES_DIR + '/' + 'upload.jpg')
    img_tgt=np.array(Image.open(UPLOAD_IMAGES_DIR+'/'+'upload.jpg').convert('RGB').resize((400,225),Image.BILINEAR))
    img_frame = np.array(Image.open(FRAME_IMAGES_DIR+'/'+tier_name))
    x_offset=0
    y_offset=0
    new_img=np.zeros((img_frame.shape[0], img_frame.shape[1], 3), np.uint8)
    new_img[y_offset:y_offset+img_tgt.shape[0], x_offset:x_offset+img_tgt.shape[1]] = img_tgt
    # 画像のオーバーレイ
    
    new_img = overlayimage(new_img, img_frame, (0, 0))
    

    img_attribute1 = np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/'+attribute1_icon+'.png').resize((35,41),Image.BILINEAR))
    new_img = overlayimage(new_img, img_attribute1, (25, 140))

    img_attribute2 = np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/'+attribute2_icon+'.png').resize((35,41),Image.BILINEAR))
    new_img = overlayimage(new_img, img_attribute2, (25, 180))

    if(int(attribute_chosen)==1):
        img_chosen=np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/chosen_attribution.png').resize((25,22),Image.BILINEAR))
        new_img = overlayimage(new_img, img_chosen, (10, 150))
    elif(int(attribute_chosen)==2):
        img_chosen=np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/chosen_attribution.png').resize((25,22),Image.BILINEAR))
        new_img = overlayimage(new_img, img_chosen, (10, 190))
    if(int(attribute_chosen)!=0):
        img_chosen_simbol=np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/chosen_simbol.png').resize((48,138),Image.BILINEAR))
        new_img = overlayimage(new_img, img_chosen_simbol, (354, 0))

    img_pil = Image.fromarray(new_img)
    draw = ImageDraw.Draw(img_pil) # drawインスタンスを生成
    message =name
    # 表示する色
    if(string_color==None):
        b,g,r,a = 255,255,255,0 #B(青)・G(緑)・R(赤)・A(透明度)：黒
    else:
        b,g,r,a = 0,0,0,0 #B(青)・G(緑)・R(赤)・A(透明度)：白
    position =  (20, 250)# テキスト表示位置
    font_name = ImageFont.truetype(FONT_M_PATH, 24)
    draw.text(position, message, font = font_name , fill = (255,255,255,0) ) # drawにテキストを記載 fill:色 BGRA

    font_attribute1 = ImageFont.truetype(FONT_M_PATH, 20)
    position_attribute1=(65, 150)
    message_attribute1=attribute1
    draw.text(position_attribute1, message_attribute1, font = font_attribute1 , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA

    font_attribute2 = ImageFont.truetype(FONT_M_PATH, 20)
    position_attribute2=(65, 190)
    message_attribute2=attribute2
    draw.text(position_attribute2, message_attribute2, font = font_attribute2 , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA

    font_tier = ImageFont.truetype(FONT_M_PATH, 24)
    position_tier=(360, 250)
    message_tier=tier
    draw.text(position_tier, message_tier, font = font_tier , fill = (255,255,255,0) ) # drawにテキストを記載 fill:色 BGRA
    img_pil=img_pil.convert('RGB')
    img_pil.save(IMAGES_DIR+'/'+'output.jpg', quality=95)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/', methods=['GET'])
def get():
	return render_template('index.html', \
		title = 'TFT Champion Pick Generator', \
		message = 'Welcome! Enter name, synergy, upload image file and select tier and synergy icons', \
        sStartFlag=True,\
        image= IMAGES_DIR+'/'+SAMPLE_IMAGE_NAME)
@app.route('/', methods=['POST'])
def post():
    tier = request.form.get('sel')
    name=request.form.get('name')
    attribute1=request.form.get('attribute1')
    attribute2=request.form.get('attribute2')
    attribute1_icon=request.form.get('attribute1_sel')
    attribute2_icon=request.form.get('attribute2_sel')
    attribute_chosen=request.form.get('attribute_chosen')
    string_color=request.form.get('string_color')
    # select_image=request.form.get('select_image')
    
    time_s = datetime.now().strftime('%Y%m%d%H%M%S')
    upfile = request.files.get('upfile', None)
    try:
        imagemaker(name,tier,time_s,attribute1,attribute2,attribute1_icon,attribute2_icon,upfile,string_color,attribute_chosen)
        return render_template('index.html', \
            title = 'TFT Champion Pick Generator', \
            message='Generated!',\
            sStartFlag=False)
            # image= IMAGES_DIR+'/'+'output'+'_'+time_s+'.jpg')
    except:
        return render_template('index.html', \
            title = 'TFT Champion Pick Generator', \
            message = 'Please Input All Form',\
            sStartFlag=True,\
            image= IMAGES_DIR+'/'+SAMPLE_IMAGE_NAME)