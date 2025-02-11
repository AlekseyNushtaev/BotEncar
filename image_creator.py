from PIL import Image


def image_creator(img_1, img_2, name):
    img_01 = Image.open(img_1)
    img_02 = Image.open(img_2)

    img_01_size = img_01.size

    new_im = Image.new('RGB', (img_01_size[0], 2*img_01_size[1]), (250,250,250))
    new_im.paste(img_01, (0,0))
    new_im.paste(img_02, (0,img_01_size[1]))
    new_im.save(f"picres/{name}.png", "PNG")

def image_all():
    for i in range(9):
        image_creator(f"pics/{i*2 + 1}.jpg", f"pics/{i*2 + 2}.jpg", i + 1)
