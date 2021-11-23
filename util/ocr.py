import ddddocr
import io
from PIL import Image

def _image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def do_ocr(image:Image):
    # recognize the image
    ocr = ddddocr.DdddOcr()
    img_bytes = _image_to_byte_array(image)
    ocr_res = ocr.classification(img_bytes)
    print("读取结果：", ocr_res)
    return ocr_res