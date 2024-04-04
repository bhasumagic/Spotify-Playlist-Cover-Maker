import requests
from io import BytesIO
from PIL import Image
    
def get_image(url,width,height):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = BytesIO(response.content)
            image = Image.open(image_bytes)
        else:
            return None
    except Exception as e:
        print(e)
        return None
        
    image = image.resize((width,height))        
    return image


def create_collage(image_list, n,size):
    collage_width = collage_height = size  # Adjust this size as needed
    collage = Image.new('RGB', (collage_width * n, collage_height * n))
    for i in range(n):
        for j in range(n):
            index = i * n + j
            img = image_list[index]
            img = img.resize((collage_width, collage_height), Image.LANCZOS)
            collage.paste(img, (j * collage_width, i * collage_height))
            
    collage = collage.resize((2000,2000))
    return collage