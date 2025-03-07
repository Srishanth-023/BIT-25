import os
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

REFERENCE_DIR = "reference_faces"
TRANSFORMED_DIR = "transformed_faces"

os.makedirs(TRANSFORMED_DIR, exist_ok=True)

def add_noise(image, amount=0.1):
    img_array = np.array(image, dtype=np.uint8)  
    num_pixels = int(amount * img_array.size)

    for _ in range(num_pixels):
        y, x = np.random.randint(0, img_array.shape[0]), np.random.randint(0, img_array.shape[1])
        img_array[y, x] = np.clip(np.random.randint(0, 256), 0, 255)

    return Image.fromarray(img_array, mode="RGB")

def distort_image(image):
    w, h = image.size
    x_shift = random.randint(-w // 3, w // 3)
    y_shift = random.randint(-h // 3, h // 3)
    return image.transform((w, h), Image.AFFINE, (1, random.uniform(-0.5, 0.5), x_shift, random.uniform(-0.5, 0.5), 1, y_shift))

def pixel_shuffle(image, intensity=0.3):
    img_array = np.array(image, dtype=np.uint8)
    h, w, _ = img_array.shape
    num_pixels = int(h * w * intensity)

    for _ in range(num_pixels):
        y1, x1 = np.random.randint(0, h), np.random.randint(0, w)
        y2, x2 = np.random.randint(0, h), np.random.randint(0, w)
        img_array[y1, x1], img_array[y2, x2] = img_array[y2, x2], img_array[y1, x1]

    return Image.fromarray(img_array, mode="RGB")

def occlude_image(image):
    img_array = np.array(image, dtype=np.uint8)
    h, w, _ = img_array.shape
    mask_h, mask_w = random.randint(h//10, h//3), random.randint(w//10, w//3)
    start_y, start_x = random.randint(0, h - mask_h), random.randint(0, w - mask_w)
    img_array[start_y:start_y+mask_h, start_x:start_x+mask_w] = 0  # Black box occlusion
    return Image.fromarray(img_array, mode="RGB")

def transform_image(image, index):
    transformations = [
        lambda img: img.rotate(random.randint(-180, 180)),
        lambda img: ImageEnhance.Brightness(img).enhance(random.uniform(0.05, 3.0)),
        lambda img: ImageEnhance.Contrast(img).enhance(random.uniform(0.1, 4.0)),
        lambda img: ImageEnhance.Sharpness(img).enhance(random.uniform(0.0, 10.0)),
        lambda img: img.filter(ImageFilter.GaussianBlur(radius=random.uniform(3, 8))),
        lambda img: add_noise(img, amount=random.uniform(0.05, 0.2)),
        lambda img: img.convert("L").convert("RGB"),
        lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
        lambda img: distort_image(img),
        lambda img: img.filter(ImageFilter.FIND_EDGES),
        lambda img: img.filter(ImageFilter.EMBOSS),
        lambda img: pixel_shuffle(img, intensity=random.uniform(0.1, 0.5)),
        lambda img: occlude_image(img)
    ]
    
    random.shuffle(transformations)
    num_transforms = random.randint(2, 5)  # Apply 2 to 5 transformations per image
    
    for transform in transformations[:num_transforms]:
        image = transform(image)
    
    return image

for filename in os.listdir(REFERENCE_DIR):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(REFERENCE_DIR, filename)
        student_name = os.path.splitext(filename)[0]

        image = Image.open(img_path).convert("RGB")
        student_folder = os.path.join(TRANSFORMED_DIR, student_name)
        os.makedirs(student_folder, exist_ok=True)

        for i in range(100):
            transformed_image = transform_image(image.copy(), i)
            transformed_image.save(os.path.join(student_folder, f"{student_name}_{i+1}.jpg"))

        print(f"Saved 100 distorted images for {student_name}")

print("Extreme transformation process completed.")