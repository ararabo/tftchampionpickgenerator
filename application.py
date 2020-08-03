from flask import Flask,render_template, request

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
ATTRIBUTE_IMAGES_DIR='./static/attribute_images'
SPLASH_IMAGES_DIR='./static/splash_images'
# フォント設置
FONT_PATH ='./static/font/YuGothM.TTC'
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

def imagemaker(name,tier,time_s,attribute1,attribute2,attribute1_icon,attribute2_icon,select_image):
    tier_name='tier'+str(tier)+'_frame.png'
    img_tgt=np.array(Image.open(SPLASH_IMAGES_DIR+'/'+select_image+'.jpg').resize((400,225),Image.BILINEAR))
    img_frame = np.array(Image.open(FRAME_IMAGES_DIR+'/'+tier_name))

    # img_tgt=cv2.resize(img_tgt,(400,225))
    x_offset=0
    y_offset=0
    new_img=np.zeros((img_frame.shape[0], img_frame.shape[1], 3), np.uint8)
    new_img[y_offset:y_offset+img_tgt.shape[0], x_offset:x_offset+img_tgt.shape[1]] = img_tgt
    # 画像のオーバーレイ
    
    new_img = overlayimage(new_img, img_frame, (0, 0))
    

    img_attribute1 = np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/'+attribute1_icon+'.png').resize((37,37),Image.BILINEAR))
    new_img = overlayimage(new_img, img_attribute1, (15, 180))

    img_attribute2 = np.array(Image.open(ATTRIBUTE_IMAGES_DIR+'/'+attribute2_icon+'.png').resize((37,37),Image.BILINEAR))
    # img_attribute1=cv2.imread(ATTRIBUTE_IMAGES_DIR+'/'+ATTRIBUTE_IMAGES_NAME1,cv2.IMREAD_UNCHANGED)
    # img_attribute1=np.resize(img_attribute1,(int(img_attribute1.shape[0]/2.5),int(img_attribute1.shape[1]/2.5)))
    new_img = overlayimage(new_img, img_attribute2, (15, 140))

    img_pil = Image.fromarray(new_img)
    draw = ImageDraw.Draw(img_pil) # drawインスタンスを生成
    message =name
    # 表示する色
    b,g,r,a = 255,255,255,0 #B(青)・G(緑)・R(赤)・A(透明度)
    font = ImageFont.truetype(FONT_PATH, 24)
    position =  (15, 245)# テキスト表示位置
    draw.text(position, message, font = font , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA

    font_attribute1 = ImageFont.truetype(FONT_PATH, 16)
    position_attribute1=(55, 190)
    message_attribute1=attribute1
    draw.text(position_attribute1, message_attribute1, font = font_attribute1 , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA

    font_attribute2 = ImageFont.truetype(FONT_PATH, 16)
    position_attribute2=(55, 150)
    message_attribute2=attribute2
    draw.text(position_attribute2, message_attribute2, font = font_attribute2 , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA

    font_tier = ImageFont.truetype(FONT_PATH, 24)
    position_tier=(360, 250)
    message_tier=tier
    draw.text(position_tier, message_tier, font = font_tier , fill = (b, g, r, a) ) # drawにテキストを記載 fill:色 BGRA
    img_pil=img_pil.convert('RGB')
    img_pil.save(IMAGES_DIR+'/'+'output.jpg', quality=95)
@app.route('/', methods=['GET'])
def get():
	return render_template('index.html', \
		title = 'TFT Champion Pick Generator', \
		message = 'Welcome!', \
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
    select_image=request.form.get('select_image')
    time_s = datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        imagemaker(name,tier,time_s,attribute1,attribute2,attribute1_icon,attribute2_icon,select_image)
        return render_template('index.html', \
            title = 'TFT Champion Pick Generator', \
            message='Generated!',\
            sStartFlag=False)
            # image= IMAGES_DIR+'/'+'output'+'_'+time_s+'.jpg')
    except:
        return render_template('index.html', \
            title = 'TFT Champion Pick Generator', \
            message = 'Please Input All Form',\
            sStartFlag=False,\
            image= IMAGES_DIR+'/'+SAMPLE_IMAGE_NAME)