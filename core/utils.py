import os
import requests
import uuid
from django.conf import settings

def download_and_save_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'generated_images'), exist_ok=True)
            filename = f'energy_fault_{uuid.uuid4().hex[:8]}.png'
            file_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return f'{settings.MEDIA_URL}generated_images/{filename}'
    except Exception as e:
        print(f'Error saving image: {e}')
    return None
