#!/usr/bin/env python3
"""
Data augmentation avanzata per object detection
"""

import torch
import torchvision.transforms.functional as F
import random
import numpy as np
from PIL import Image, ImageFilter
from utils_obj import photometric_distort, expand, random_crop, flip, resize

def advanced_transform(image, boxes, labels, difficulties, split, config=None):
    """
    Trasformazione avanzata con data augmentation migliorata
    
    :param image: immagine PIL
    :param boxes: bounding boxes, tensor (n_objects, 4)
    :param labels: labels, tensor (n_objects)
    :param difficulties: difficulties, tensor (n_objects)
    :param split: 'TRAIN' o 'TEST'
    :param config: configurazione con parametri di augmentation
    :return: immagine e annotazioni trasformate
    """
    assert split in {'TRAIN', 'TEST', 'train', 'valid'}
    
    # Logging counter per advanced augmentation
    if not hasattr(advanced_transform, 'call_count'):
        advanced_transform.call_count = 0
    advanced_transform.call_count += 1
    
    # Normalizzazione ImageNet
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    new_image = image
    new_boxes = boxes
    new_labels = labels
    new_difficulties = difficulties
    
    # Applica augmentation solo durante il training
    if split.upper() == 'TRAIN':
        # Logging ogni 100 chiamate per confermare l'uso
        if advanced_transform.call_count % 100 == 1:
            print(f"✨ Advanced data augmentation applicata (chiamata #{advanced_transform.call_count})")
        
        # 1. Data augmentation avanzata (prima delle trasformazioni geometriche)
        if config and hasattr(config, 'advanced_augmentation') and config.advanced_augmentation:
            new_image = apply_advanced_color_augmentation(new_image, config)
            new_image = apply_noise_and_blur(new_image, config)
            
            # Cutout solo se ci sono bounding box
            if len(boxes) > 0:
                new_image = apply_cutout(new_image, boxes, config)
        
        # 2. Distorsioni fotometriche standard
        new_image = photometric_distort(new_image)

        # 3. Converti in tensor per trasformazioni geometriche
        new_image = F.to_tensor(new_image)

        # 4. Expand (zoom out)
        if random.random() < 0.5:
            new_image, new_boxes = expand(new_image, boxes, filler=mean)

        # 5. Random crop (zoom in)
        new_image, new_boxes, new_labels, new_difficulties = random_crop(
            new_image, new_boxes, new_labels, new_difficulties
        )

        # 6. Converti in PIL per flip
        new_image = F.to_pil_image(new_image)

        # 7. Flip orizzontale
        if random.random() < 0.5:
            new_image, new_boxes = flip(new_image, new_boxes)

    # 8. Resize finale a 300x300
    new_image, new_boxes = resize(new_image, new_boxes, dims=(300, 300))

    # 9. Converti in tensor e normalizza
    new_image = F.to_tensor(new_image)
    new_image = F.normalize(new_image, mean=mean, std=std)

    return new_image, new_boxes, new_labels, new_difficulties


def apply_advanced_color_augmentation(image, config):
    """Applica color augmentation avanzata"""
    if random.random() < 0.8:
        params = config.augmentation_params
        
        # Brightness con range più ampio
        if random.random() < 0.6:
            brightness_factor = random.uniform(*params['brightness_range'])
            image = F.adjust_brightness(image, brightness_factor)
        
        # Contrast
        if random.random() < 0.6:
            contrast_factor = random.uniform(*params['contrast_range'])
            image = F.adjust_contrast(image, contrast_factor)
        
        # Saturation
        if random.random() < 0.5:
            saturation_factor = random.uniform(*params['saturation_range'])
            image = F.adjust_saturation(image, saturation_factor)
        
        # Hue (più conservativo)
        if random.random() < 0.3:
            hue_factor = random.uniform(*params['hue_range'])
            image = F.adjust_hue(image, hue_factor)
    
    return image


def apply_noise_and_blur(image, config):
    """Applica rumore e blur"""
    params = config.augmentation_params
    
    # Blur gaussiano
    if random.random() < params['blur_probability']:
        blur_radius = random.uniform(0.5, 1.5)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Rumore gaussiano
    if random.random() < params['noise_probability']:
        img_array = np.array(image)
        
        # Rumore più leggero per non compromettere troppo l'immagine
        noise_std = random.uniform(3, 8)
        noise = np.random.normal(0, noise_std, img_array.shape).astype(np.int16)
        
        # Applica rumore e limita i valori
        noisy_img = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        image = Image.fromarray(noisy_img)
    
    return image


def apply_cutout(image, boxes, config):
    """Applica cutout evitando le zone degli oggetti"""
    if random.random() < config.augmentation_params['cutout_probability']:
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        # Numero di patch cutout
        num_patches = random.randint(1, 3)
        
        for _ in range(num_patches):
            # Dimensioni del patch (3-10% dell'immagine)
            patch_h = random.randint(int(h * 0.03), int(h * 0.10))
            patch_w = random.randint(int(w * 0.03), int(w * 0.10))
            
            # Trova una posizione che non si sovrapponga troppo con gli oggetti
            best_pos = None
            min_overlap = float('inf')
            
            for attempt in range(15):  # Massimo 15 tentativi
                y = random.randint(0, h - patch_h)
                x = random.randint(0, w - patch_w)
                
                # Calcola sovrapposizione con tutte le bounding box
                patch_box = [x/w, y/h, (x+patch_w)/w, (y+patch_h)/h]
                total_overlap = 0
                
                for box in boxes:
                    if len(box) >= 4:
                        overlap = calculate_box_overlap(patch_box, box.tolist())
                        total_overlap += overlap
                
                # Scegli la posizione con meno sovrapposizione
                if total_overlap < min_overlap:
                    min_overlap = total_overlap
                    best_pos = (x, y)
                
                # Se trovata una posizione con sovrapposizione minima, usala
                if total_overlap < 0.05:  # Meno del 5% di sovrapposizione
                    break
            
            # Applica cutout nella migliore posizione trovata
            if best_pos and min_overlap < 0.3:  # Solo se sovrapposizione < 30%
                x, y = best_pos
                
                # Colore di riempimento casuale (grigio)
                fill_color = random.randint(64, 192)
                img_array[y:y+patch_h, x:x+patch_w] = fill_color
        
        image = Image.fromarray(img_array)
    
    return image


def calculate_box_overlap(box1, box2):
    """Calcola l'area di sovrapposizione tra due bounding box"""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Area di intersezione
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return 0.0
    
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    
    # Area della seconda box (oggetto)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    
    # Frazione dell'oggetto coperta dal cutout
    if box2_area > 0:
        return inter_area / box2_area
    else:
        return 0.0


def mixup_data(images, labels, alpha=0.2):
    """
    Applica MixUp tra batch di immagini
    Nota: Questa è una versione semplificata per object detection
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = images.size(0)
    index = torch.randperm(batch_size)

    mixed_images = lam * images + (1 - lam) * images[index, :]
    
    return mixed_images, labels, index, lam


def get_augmentation_stats(config):
    """Restituisce statistiche sui parametri di augmentation"""
    if not hasattr(config, 'augmentation_params'):
        return "Nessun parametro di augmentation configurato"
    
    params = config.augmentation_params
    stats = []
    stats.append("🎨 Parametri Data Augmentation:")
    stats.append(f"  - Brightness range: {params['brightness_range']}")
    stats.append(f"  - Contrast range: {params['contrast_range']}")
    stats.append(f"  - Saturation range: {params['saturation_range']}")
    stats.append(f"  - Hue range: {params['hue_range']}")
    stats.append(f"  - Blur probability: {params['blur_probability']}")
    stats.append(f"  - Noise probability: {params['noise_probability']}")
    stats.append(f"  - Cutout probability: {params['cutout_probability']}")
    stats.append(f"  - Rotation range: {params['rotation_range']}")
    
    return "\n".join(stats)
