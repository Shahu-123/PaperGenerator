from __future__ import division
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import io
import boto3

# function to merge 2 images vertically
def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=False):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
    dst = Image.new('RGB', (_im1.width, _im1.height + _im2.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height))
    return dst

# Function to merge n number of images into one vertical image
def a4(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

def old_img(lst, final=[]):
    qp_list = lst.copy()
    final.extend([x for x in qp_list if x.height > 1300])
    for image in final:
        if image in qp_list:
            qp_list.remove(image)
    qp_list_2 = []
    if len(qp_list) % 2 != 0:
        qp_list_2.append(qp_list[-1])
        qp_list.pop(-1)
    for x in range(0, len(qp_list), 2):
        qp_list_2.append(get_concat_v_resize(qp_list[x], qp_list[x+1]))
    if len(qp_list_2) == 1:
        final.append(qp_list_2[0])
        qp_list_2.pop(0)
        return final
    if len(qp_list_2) == 0:
        return final
    old_img(qp_list_2, final)
    return final


def new_img(lst):
    qp_list = lst.copy()
    i = 0
    while i < len(qp_list)-1:
        if (qp_list[i].height + qp_list[i + 1].height) < 2000:
            qp_list[i] = get_concat_v_resize(qp_list[i], qp_list[i + 1])
            qp_list.pop(i+1)
        else:
            i += 1
    return qp_list

def add_numbers(img_list, info_str_list, info_print):
     # Initialize S3 client
    s3 = boto3.client('s3')

    # Download the SQLite database file from S3
    s3_bucket = 'shahu-exam'
    s3.download_file(s3_bucket, 'Arial Bold.ttf', '/tmp/Arial Bold.ttf')
    s3.download_file(s3_bucket, 'Arial Italic.ttf', '/tmp/Arial Italic.ttf')
    
    # Use a truetype font and specify a size. Adjust the font path as necessary.
    font = ImageFont.truetype("/tmp/Arial Bold.ttf", 30)  # Using Arial font with a size of 30
    info_font = ImageFont.truetype("/tmp/Arial Italic.ttf", 15)  # Using Arial font with a size of 10

    for i, image in enumerate(img_list):
        w, h = image.size

        # Create a drawing context for the image
        draw = ImageDraw.Draw(image)

        # Calculate position and size based on whether it's a single-digit or double-digit number
        if i + 1 < 10:
            position = (int(w * 0.08162), 10)
        else:
            position = (int(w * 0.08162) - 15, 10)  # Adjust the position slightly for two digits

        # Draw the number on the image
        draw.text(position, str(i + 1), fill="black", font=font)  # Adjust fill color if needed
        if info_print:
            # Draw the info_str right next to the number. Adjust as needed:
            info_position = (w - 200, h-40)
            draw.text(info_position, info_str_list[i], fill="black", font=info_font)

    return img_list

def add_tag(img_list):
    db_dir = '/tmp/my-database.db'
    with sqlite3.connect(db_dir) as connection:
        command = "SELECT Image FROM Tags"
        cursor = connection.execute(command)
        data = cursor.fetchall()
        tag = data[0][0]
    for i in range(len(img_list)):
        image = img_list[i]
        w, h = image.size
        tag2 = Image.open(io.BytesIO(tag))
        pil = tag2.resize((w // 5, (w // 5) // 20))
        pil_w, pil_h = pil.size
        dim = (w - pil_w - 10, h - pil_h - 5)
        image.paste(pil, (dim))
    return img_list