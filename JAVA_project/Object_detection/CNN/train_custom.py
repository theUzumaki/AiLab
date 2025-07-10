#!/usr/bin/env python3
"""
Training script per object detection con SSD personalizzato
Adattato per supportare Dataset_4 personalizzato (Dataset_4)
"""

import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
import os
import sys
import time
import json
import argparse
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import random
import torchvision.transforms.functional as F
from PIL import Image, ImageEnhance, ImageFilter

# Aggiungi il percorso corrente al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cnn import SSD300, MultiBoxLoss
from utils_obj import *
from custom_dataset import CustomDataset, create_data_loaders

# Configurazione device
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
print(f'🚀 Usando device: {device}')

# Configurazione training
class TrainingConfig:
    def __init__(self):
        # Percorsi
        self.dataset_path = './Dataset_4'  # Cambiato a Dataset_4
        self.data_folder = './data'  # Dove salvare i file JSON processati
        self.checkpoint_folder = './checkpoints'
        self.results_folder = './results'
        
        # Parametri modello - sarà aggiornato automaticamente dal dataset
        self.n_classes = 8  # Valore iniziale, sarà aggiornato da prepare_dataset
        
        # Parametri training
        self.batch_size = 2  # Ridotto per debug
        self.num_workers = 0  # Disabilitato per debug
        self.learning_rate = 1e-3
        self.decay_lr_at = [80, 100]  # Epoche per ridurre learning rate
        self.decay_lr_to = 0.1
        self.momentum = 0.9
        self.weight_decay = 5e-4
        self.num_epochs = 120
        self.print_freq = 200
        self.save_freq = 10
        
        # Parametri loss
        self.threshold = 0.5
        self.neg_pos_ratio = 3
        self.alpha = 1.0
        
        # Parametri data augmentation
        self.use_transform = True
        self.advanced_augmentation = True  # Usa augmentation avanzata
        
        # Parametri per data augmentation avanzata
        self.augmentation_params = {
            'brightness_range': (0.7, 1.3),
            'contrast_range': (0.7, 1.3),
            'saturation_range': (0.7, 1.3),
            'hue_range': (-0.05, 0.05),
            'blur_probability': 0.3,
            'noise_probability': 0.2,
            'cutout_probability': 0.2,
            'rotation_range': (-10, 10),
        }
        
        # Checkpoint
        self.resume_checkpoint = None
        self.pretrained = True
        
        # Parametri mAP
        self.min_score = 0.01  # Score minimo per detection
        self.max_overlap = 0.45  # NMS threshold
        self.top_k = 200  # Numero massimo detection per immagine
        
        # Validazione
        self.eval_freq = 5
        
        # Debug e logging
        self.debug_map = True  # Stampa informazioni debug per mAP
        
        # Crea cartelle se non esistono
        os.makedirs(self.checkpoint_folder, exist_ok=True)
        os.makedirs(self.results_folder, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)


def advanced_data_augmentation(image, boxes, labels, difficulties, config, split):
    """
    Applica data augmentation avanzata per object detection
    """
    if split != 'TRAIN' or not config.advanced_augmentation:
        return image, boxes, labels, difficulties
    
    # Color jittering avanzato
    if random.random() < 0.8:
        # Brightness
        if random.random() < 0.5:
            brightness_factor = random.uniform(*config.augmentation_params['brightness_range'])
            image = F.adjust_brightness(image, brightness_factor)
        
        # Contrast
        if random.random() < 0.5:
            contrast_factor = random.uniform(*config.augmentation_params['contrast_range'])
            image = F.adjust_contrast(image, contrast_factor)
        
        # Saturation
        if random.random() < 0.5:
            saturation_factor = random.uniform(*config.augmentation_params['saturation_range'])
            image = F.adjust_saturation(image, saturation_factor)
        
        # Hue
        if random.random() < 0.3:
            hue_factor = random.uniform(*config.augmentation_params['hue_range'])
            image = F.adjust_hue(image, hue_factor)
    
    # Blur occasionale
    if random.random() < config.augmentation_params['blur_probability']:
        radius = random.uniform(0.5, 1.5)
        image = image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    # Rumore gaussiano
    if random.random() < config.augmentation_params['noise_probability']:
        img_array = np.array(image)
        noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
        noisy_img = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        image = Image.fromarray(noisy_img)
    
    # Cutout (evitando le bounding box principali)
    if random.random() < config.augmentation_params['cutout_probability'] and len(boxes) > 0:
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        # Crea 1-2 patch di cutout
        num_patches = random.randint(1, 2)
        
        for _ in range(num_patches):
            patch_h = random.randint(int(h * 0.05), int(h * 0.12))
            patch_w = random.randint(int(w * 0.05), int(w * 0.12))
            
            # Posizione casuale, evitando il centro degli oggetti
            y = random.randint(0, h - patch_h)
            x = random.randint(0, w - patch_w)
            
            # Applica cutout con valore grigio casuale
            gray_value = random.randint(64, 192)
            img_array[y:y+patch_h, x:x+patch_w] = gray_value
        
        image = Image.fromarray(img_array)
    
    return image, boxes, labels, difficulties


def prepare_dataset(config):
    """
    Prepara il dataset convertendo dal formato YOLO al formato SSD
    """
    print('📁 Preparazione dataset...')
    
    # Verifica se i dati sono già stati processati
    train_images_path = os.path.join(config.data_folder, 'TRAIN_images.json')
    test_images_path = os.path.join(config.data_folder, 'TEST_images.json')
    
    if os.path.exists(train_images_path) and os.path.exists(test_images_path):
        print('✅ Dataset già processato, caricamento...')
        return
    
    # Processa il dataset
    print('🔄 Processamento dataset YOLO...')
    try:
        n_train, n_test, n_classes = create_yolo_data_lists(
            config.dataset_path,
            config.data_folder
        )
        
        # Aggiorna numero di classi
        config.n_classes = n_classes
        print(f'✅ Dataset processato: {n_train} training, {n_test} test, {n_classes} classi')
        
    except Exception as e:
        print(f'❌ Errore nel processamento dataset: {e}')
        sys.exit(1)


def create_model(config):
    """
    Crea il modello SSD300
    """
    print('🔧 Creazione modello SSD300...')
    
    # Crea modello
    model = SSD300(n_classes=config.n_classes)
    
    # Sposta su GPU se disponibile
    model = model.to(device)
    
    # Criterio di loss
    criterion = MultiBoxLoss(priors_cxcy=model.priors_cxcy, 
                           threshold=config.threshold,
                           neg_pos_ratio=config.neg_pos_ratio,
                           alpha=config.alpha).to(device)
    
    # Ottimizzatore
    biases = []
    not_biases = []
    for param_name, param in model.named_parameters():
        if param.requires_grad:
            if param_name.endswith('.bias'):
                biases.append(param)
            else:
                not_biases.append(param)
    
    optimizer = optim.SGD(params=[{'params': biases, 'lr': 2 * config.learning_rate},
                                 {'params': not_biases}],
                         lr=config.learning_rate, 
                         momentum=config.momentum, 
                         weight_decay=config.weight_decay)
    
    return model, criterion, optimizer


def save_checkpoint(epoch, model, optimizer, loss, config, is_best=False):
    """
    Salva checkpoint del modello
    """
    state = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'config': config.__dict__
    }
    
    if is_best:
        best_filename = os.path.join(config.checkpoint_folder, 'best_model.pth')
        torch.save(state, best_filename)
        print(f'💾 Salvato miglior modello: {best_filename}')


def load_checkpoint(checkpoint_path, model, optimizer=None):
    """
    Carica checkpoint
    """
    print(f'📥 Caricamento checkpoint: {checkpoint_path}')
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    start_epoch = checkpoint.get('epoch', 0) + 1
    best_loss = checkpoint.get('loss', float('inf'))
    
    print(f'✅ Checkpoint caricato. Riprendo dall\'epoca {start_epoch}')
    return start_epoch, best_loss


def train_epoch(model, criterion, optimizer, data_loader, epoch, config):
    """
    Addestra per una epoca
    """
    model.train()
    
    losses = []
    batch_time = []
    data_time = []
    
    start = time.time()
    
    # Progress bar
    pbar = tqdm(data_loader, desc=f'Epoca {epoch}')
    
    for i, (images, boxes, labels, _) in enumerate(pbar):
        data_time.append(time.time() - start)
        
        # Logging per confermare l'uso della data augmentation
        if i == 0 and epoch % 5 == 0:  # Log all'inizio di ogni 5 epoche
            if config.advanced_augmentation:
                print(f"\n🔄 Epoca {epoch}: Processing batch con ADVANCED data augmentation attiva")
            elif config.use_transform:
                print(f"\n📷 Epoca {epoch}: Processing batch con transform standard")
            else:
                print(f"\n⚪ Epoca {epoch}: Processing batch SENZA data augmentation")
        
        # Sposta su GPU
        images = images.to(device)  # (batch_size, 3, 300, 300)
        boxes = [b.to(device) for b in boxes]
        labels = [l.to(device) for l in labels]
        
        # Forward pass
        predicted_locs, predicted_scores = model(images)  # (N, 8732, 4), (N, 8732, n_classes)
        
        # Calcola loss
        loss = criterion(predicted_locs, predicted_scores, boxes, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Clip gradients per stabilità
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        
        # Aggiorna parametri
        optimizer.step()
        
        losses.append(loss.item())
        batch_time.append(time.time() - start)
        
        # Update progress bar
        pbar.set_postfix({
            'Loss': f'{loss.item():.4f}',
            'Avg Loss': f'{np.mean(losses):.4f}',
            'LR': f'{optimizer.param_groups[0]["lr"]:.6f}'
        })
        
        start = time.time()
        
        # Print statistics
        if i % config.print_freq == 0:
            print(f'\\nEpoca: [{epoch}][{i}/{len(data_loader)}]\\t'
                  f'Batch Time: {np.mean(batch_time[-config.print_freq:]):.3f}s\\t'
                  f'Data Time: {np.mean(data_time[-config.print_freq:]):.3f}s\\t'
                  f'Loss: {loss.item():.4f} ({np.mean(losses):.4f})')
    
    return np.mean(losses)


def move_to_cpu(data):
    """
    Sposta tensori su CPU in modo sicuro
    """
    if torch.is_tensor(data):
        return data.cpu()
    elif isinstance(data, list):
        return [move_to_cpu(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(move_to_cpu(item) for item in data)
    else:
        return data


def ensure_cpu_tensors(tensor_list, name="tensor"):
    """
    Assicura che tutti i tensori in una lista siano su CPU
    """
    cpu_tensors = []
    for i, tensor in enumerate(tensor_list):
        if torch.is_tensor(tensor):
            if tensor.device.type != 'cpu':
                tensor = tensor.cpu()
            cpu_tensors.append(tensor)
        else:
            print(f"⚠️  Warning: {name}[{i}] non è un tensore: {type(tensor)}")
            cpu_tensors.append(tensor)
    return cpu_tensors


def calculate_validation_map(model, data_loader, config):
    """
    Calcola mAP sul dataset di validazione
    """
    model.eval()
    
    det_boxes = []
    det_labels = []
    det_scores = []
    true_boxes = []
    true_labels = []
    true_difficulties = []
    
    with torch.no_grad():
        pbar = tqdm(data_loader, desc='Calcolo mAP')
        
        for i, (images, boxes, labels, difficulties) in enumerate(pbar):
            # Sposta su GPU
            images = images.to(device)
            
            # Forward pass
            predicted_locs, predicted_scores = model(images)
            
            # Detect objects
            det_boxes_batch, det_labels_batch, det_scores_batch = model.detect_objects(
                predicted_locs, predicted_scores, 
                min_score=config.min_score, max_overlap=config.max_overlap, top_k=config.top_k
            )
            
            # Sposta detection su CPU e aggiungi alle liste
            det_boxes.extend(move_to_cpu(det_boxes_batch))
            det_labels.extend(move_to_cpu(det_labels_batch))
            det_scores.extend(move_to_cpu(det_scores_batch))
            
            # Sposta ground truth su CPU e aggiungi alle liste
            true_boxes.extend(move_to_cpu(boxes))
            true_labels.extend(move_to_cpu(labels))
            true_difficulties.extend(move_to_cpu(difficulties))
    
    # Calcola mAP (tutti i tensori sono già su CPU)
    if len(det_boxes) > 0:
        # Doppia verifica che tutti i tensori siano su CPU
        det_boxes = ensure_cpu_tensors(det_boxes, "det_boxes")
        det_labels = ensure_cpu_tensors(det_labels, "det_labels") 
        det_scores = ensure_cpu_tensors(det_scores, "det_scores")
        true_boxes = ensure_cpu_tensors(true_boxes, "true_boxes")
        true_labels = ensure_cpu_tensors(true_labels, "true_labels")
        true_difficulties = ensure_cpu_tensors(true_difficulties, "true_difficulties")
        
        if config.debug_map:
            print(f"🔍 Debug mAP: {len(det_boxes)} detection, {len(true_boxes)} ground truth")
            if det_boxes:
                print(f"  - Detection tensor device: {det_boxes[0].device if torch.is_tensor(det_boxes[0]) else 'Non-tensor'}")
            if true_boxes:
                print(f"  - True tensor device: {true_boxes[0].device if torch.is_tensor(true_boxes[0]) else 'Non-tensor'}")
        
        try:
            # Usa la versione CPU-only di calculate_mAP
            APs, mAP = calculate_mAP_cpu(det_boxes, det_labels, det_scores, 
                                        true_boxes, true_labels, true_difficulties)
            return APs, mAP
        except Exception as e:
            print(f"❌ Errore nel calcolo mAP: {e}")
            if config.debug_map:
                print("🔍 Debug dettagliato:")
                print(f"  - len(det_boxes): {len(det_boxes)}")
                print(f"  - len(true_boxes): {len(true_boxes)}")
                if det_boxes:
                    print(f"  - type(det_boxes[0]): {type(det_boxes[0])}")
                if true_boxes:
                    print(f"  - type(true_boxes[0]): {type(true_boxes[0])}")
            return {}, 0.0
    else:
        print("⚠️  Nessuna detection trovata")
        return {}, 0.0


def validate_epoch(model, criterion, data_loader, epoch, config):
    """
    Valida il modello calcolando sia loss che mAP
    """
    model.eval()
    
    losses = []
    
    with torch.no_grad():
        pbar = tqdm(data_loader, desc=f'Validazione Epoca {epoch}')
        
        for i, (images, boxes, labels, _) in enumerate(pbar):
            # Sposta su GPU
            images = images.to(device)
            boxes = [b.to(device) for b in boxes]
            labels = [l.to(device) for l in labels]
            
            # Forward pass
            predicted_locs, predicted_scores = model(images)
            
            # Calcola loss
            loss = criterion(predicted_locs, predicted_scores, boxes, labels)
            losses.append(loss.item())
            
            pbar.set_postfix({'Val Loss': f'{loss.item():.4f}'})
    
    avg_loss = np.mean(losses)
    
    # Calcola mAP ogni poche epoche per non rallentare troppo
    if epoch % (config.eval_freq * 2) == 0:
        print(f'\n📊 Calcolo mAP per epoca {epoch}...')
        APs, mAP = calculate_validation_map(model, data_loader, config)
        
        print(f'🎯 mAP: {mAP:.4f}')
        print('📈 Average Precision per classe:')
        for class_name, ap in APs.items():
            print(f'  - {class_name}: {ap:.4f}')
        
        return avg_loss, mAP, APs
    
    return avg_loss, None, None


def adjust_learning_rate(optimizer, scale):
    """
    Riduce learning rate di un fattore 'scale'
    """
    for param_group in optimizer.param_groups:
        param_group['lr'] = param_group['lr'] * scale
    print(f'🔄 Learning rate ridotto a {optimizer.param_groups[0]["lr"]:.6f}')


def plot_training_history(train_losses, val_losses, map_scores=None, config=None):
    """
    Plotta la storia del training incluso mAP se disponibile
    """
    if map_scores and len(map_scores) > 0:
        fig, axes = plt.subplots(1, 3, figsize=(18, 4))
        
        # Loss plot
        axes[0].plot(train_losses, label='Training Loss')
        axes[0].plot(val_losses, label='Validation Loss')
        axes[0].set_title('Loss durante il Training')
        axes[0].set_xlabel('Epoca')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # Training loss only
        axes[1].plot(train_losses, label='Training Loss')
        axes[1].set_title('Training Loss')
        axes[1].set_xlabel('Epoca')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        # mAP plot
        map_epochs = list(range(0, len(map_scores) * (config.eval_freq * 2), config.eval_freq * 2))
        axes[2].plot(map_epochs[:len(map_scores)], map_scores, 'ro-', label='mAP')
        axes[2].set_title('Mean Average Precision (mAP)')
        axes[2].set_xlabel('Epoca')
        axes[2].set_ylabel('mAP')
        axes[2].legend()
        axes[2].grid(True)
        
    else:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        axes[0].plot(train_losses, label='Training Loss')
        axes[0].plot(val_losses, label='Validation Loss')
        axes[0].set_title('Loss durante il Training')
        axes[0].set_xlabel('Epoca')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        axes[1].plot(train_losses, label='Training Loss')
        axes[1].set_title('Training Loss')
        axes[1].set_xlabel('Epoca')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
    
    plt.tight_layout()
    if config:
        plt.savefig(os.path.join(config.results_folder, 'training_history.png'))
    plt.show()


def save_map_results(map_scores, APs_history, config):
    """
    Salva i risultati mAP in un file JSON
    """
    results = {
        'map_scores': map_scores,
        'final_map': max(map_scores) if map_scores else 0.0,
        'APs_history': APs_history,
        'config': {
            'min_score': config.min_score,
            'max_overlap': config.max_overlap,
            'top_k': config.top_k,
            'eval_freq': config.eval_freq
        }
    }
    
    results_path = os.path.join(config.results_folder, 'map_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f'📊 Risultati mAP salvati in: {results_path}')


def calculate_mAP_cpu(det_boxes, det_labels, det_scores, true_boxes, true_labels, true_difficulties):
    """
    Versione di calculate_mAP che funziona sempre su CPU
    """
    assert len(det_boxes) == len(det_labels) == len(det_scores) == len(true_boxes) == len(
        true_labels) == len(true_difficulties)
    
    # Controlla se ci sono detection e ground truth
    if len(det_boxes) == 0 or len(true_boxes) == 0:
        return {}, 0.0
    
    # Usa sempre CPU per il calcolo mAP
    cpu_device = torch.device('cpu')
    n_classes = len(label_map)

    # Store all (true) objects in a single continuous tensor while keeping track of the image it is from
    true_images = list()
    for i in range(len(true_labels)):
        if true_labels[i].numel() > 0:  # Controlla che il tensore non sia vuoto
            true_images.extend([i] * true_labels[i].size(0))
    
    if len(true_images) == 0:
        return {}, 0.0
        
    true_images = torch.LongTensor(true_images).to(cpu_device)  # Forza CPU
    true_boxes = torch.cat([box for box in true_boxes if box.numel() > 0], dim=0).to(cpu_device)  # Forza CPU
    true_labels = torch.cat([label for label in true_labels if label.numel() > 0], dim=0).to(cpu_device)  # Forza CPU
    true_difficulties = torch.cat([diff for diff in true_difficulties if diff.numel() > 0], dim=0).to(cpu_device)  # Forza CPU

    assert true_images.size(0) == true_boxes.size(0) == true_labels.size(0)

    # Store all detections in a single continuous tensor while keeping track of the image it is from
    det_images = list()
    for i in range(len(det_labels)):
        if det_labels[i].numel() > 0:  # Controlla che il tensore non sia vuoto
            det_images.extend([i] * det_labels[i].size(0))
    
    if len(det_images) == 0:
        return {}, 0.0
        
    det_images = torch.LongTensor(det_images).to(cpu_device)  # Forza CPU
    det_boxes = torch.cat([box for box in det_boxes if box.numel() > 0], dim=0).to(cpu_device)  # Forza CPU
    det_labels = torch.cat([label for label in det_labels if label.numel() > 0], dim=0).to(cpu_device)  # Forza CPU
    det_scores = torch.cat([score for score in det_scores if score.numel() > 0], dim=0).to(cpu_device)  # Forza CPU

    assert det_images.size(0) == det_boxes.size(0) == det_labels.size(0) == det_scores.size(0)

    # Calculate APs for each class (except background)
    average_precisions = torch.zeros((n_classes - 1), dtype=torch.float).to(cpu_device)
    for c in range(1, n_classes):
        # Extract only objects with this class
        true_class_images = true_images[true_labels == c]
        true_class_boxes = true_boxes[true_labels == c]
        true_class_difficulties = true_difficulties[true_labels == c]
        n_easy_class_objects = (1 - true_class_difficulties).sum().item()

        # Keep track of which true objects with this class have already been 'detected'
        true_class_boxes_detected = torch.zeros((true_class_difficulties.size(0)), dtype=torch.uint8).to(cpu_device)

        # Extract only detections with this class
        det_class_images = det_images[det_labels == c]
        det_class_boxes = det_boxes[det_labels == c]
        det_class_scores = det_scores[det_labels == c]
        n_class_detections = det_class_boxes.size(0)
        if n_class_detections == 0:
            continue

        # Sort detections in decreasing order of confidence/scores
        det_class_scores, sort_ind = torch.sort(det_class_scores, dim=0, descending=True)
        det_class_images = det_class_images[sort_ind]
        det_class_boxes = det_class_boxes[sort_ind]

        # In the order of decreasing scores, check if true or false positive
        true_positives = torch.zeros((n_class_detections), dtype=torch.float).to(cpu_device)
        false_positives = torch.zeros((n_class_detections), dtype=torch.float).to(cpu_device)
        for d in range(n_class_detections):
            this_detection_box = det_class_boxes[d].unsqueeze(0)
            this_image = det_class_images[d]

            # Find objects in the same image with this class, their difficulties, and whether they have been detected before
            object_boxes = true_class_boxes[true_class_images == this_image]
            object_difficulties = true_class_difficulties[true_class_images == this_image]
            
            # If no such object in this image, then the detection is a false positive
            if object_boxes.size(0) == 0:
                false_positives[d] = 1
                continue

            # Find maximum overlap of this detection with objects in this image of this class
            overlaps = find_jaccard_overlap(this_detection_box, object_boxes)
            max_overlap, ind = torch.max(overlaps.squeeze(0), dim=0)

            # 'ind' is the index of the object in these image-level tensors 'object_boxes', 'object_difficulties'
            # In the original class-level tensors 'true_class_boxes', etc., 'ind' corresponds to object with index...
            original_ind = torch.LongTensor(range(true_class_boxes.size(0)))[true_class_images == this_image][ind]

            # If the maximum overlap is greater than the threshold of 0.5, it's a match
            if max_overlap.item() > 0.5:
                # If the object it matched with is 'difficult', ignore it
                if object_difficulties[ind] == 0:
                    # If this object has already not been detected, it's a true positive
                    if true_class_boxes_detected[original_ind] == 0:
                        true_positives[d] = 1
                        true_class_boxes_detected[original_ind] = 1
                    # Otherwise, it's a false positive (since this object is already accounted for)
                    else:
                        false_positives[d] = 1
            # Otherwise, the detection occurs in a different location than the actual object, and is a false positive
            else:
                false_positives[d] = 1

        # Compute cumulative precision and recall at each detection in the order of decreasing scores
        cumul_true_positives = torch.cumsum(true_positives, dim=0)
        cumul_false_positives = torch.cumsum(false_positives, dim=0)
        cumul_precision = cumul_true_positives / (cumul_true_positives + cumul_false_positives + 1e-10)
        cumul_recall = cumul_true_positives / n_easy_class_objects

        # Find the mean of the maximum of the precisions corresponding to recalls above the threshold 't'
        recall_thresholds = torch.arange(start=0, end=1.1, step=.1).tolist()
        precisions = torch.zeros((len(recall_thresholds)), dtype=torch.float).to(cpu_device)
        for i, t in enumerate(recall_thresholds):
            recalls_above_t = cumul_recall >= t
            if recalls_above_t.any():
                precisions[i] = cumul_precision[recalls_above_t].max()
            else:
                precisions[i] = 0.
        average_precisions[c - 1] = precisions.mean()

    # Calculate Mean Average Precision (mAP)
    mean_average_precision = average_precisions.mean().item()

    # Keep class-wise average precisions in a dictionary
    average_precisions = {rev_label_map[c + 1]: v for c, v in enumerate(average_precisions.tolist())}

    return average_precisions, mean_average_precision


def main():
    # Parsing argomenti
    parser = argparse.ArgumentParser(description='Training SSD300 per object detection')
    parser.add_argument('--dataset_path', type=str, default='./Dataset_4',
                       help='Percorso dataset')
    parser.add_argument('--batch_size', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--num_epochs', type=int, default=120,
                       help='Numero di epoche')
    parser.add_argument('--learning_rate', type=float, default=1e-3,
                       help='Learning rate iniziale')
    parser.add_argument('--resume', type=str, default=None,
                       help='Percorso checkpoint da cui riprendere')
    parser.add_argument('--no_advanced_aug', action='store_true',
                       help='Disabilita data augmentation avanzata')
    parser.add_argument('--eval_only', action='store_true',
                       help='Solo valutazione, no training')
    
    args = parser.parse_args()
    
    # Configurazione
    config = TrainingConfig()
    config.dataset_path = args.dataset_path
    config.batch_size = args.batch_size
    config.num_epochs = args.num_epochs
    config.learning_rate = args.learning_rate
    config.resume_checkpoint = args.resume
    
    # Disabilita augmentation avanzata se richiesto
    if args.no_advanced_aug:
        config.advanced_augmentation = False
        print('⚠️  Data augmentation avanzata DISABILITATA')
    
    print('🎯 Configurazione Training:')
    print(f'  - Dataset: {config.dataset_path}')
    print(f'  - Batch size: {config.batch_size}')
    print(f'  - Epoche: {config.num_epochs}')
    print(f'  - Learning rate: {config.learning_rate}')
    print(f'  - Device: {device}')
    
    # Logging dettagliato per data augmentation
    if config.advanced_augmentation:
        print(f'  ✨ ADVANCED DATA AUGMENTATION: ATTIVA')
        print(f'     📊 Parametri configurati:')
        for key, value in config.augmentation_params.items():
            print(f'       - {key}: {value}')
    elif config.use_transform:
        print(f'  📷 Transform standard: ATTIVA')
    else:
        print(f'  ⚪ Data augmentation: DISATTIVA')
    
    # Stampa parametri di augmentation se abilitata
    if config.advanced_augmentation:
        from augmentation import get_augmentation_stats
        print(get_augmentation_stats(config))
    
    # Prepara dataset
    prepare_dataset(config)
    
    # Crea data loaders
    print('📊 Creazione data loaders...')
    
    # Prima verifica che i dati esistano
    train_images_path = os.path.join(config.data_folder, 'TRAIN_images.json')
    test_images_path = os.path.join(config.data_folder, 'TEST_images.json')
    
    if not os.path.exists(train_images_path):
        print(f'❌ File non trovato: {train_images_path}')
        sys.exit(1)
    
    if not os.path.exists(test_images_path):
        print(f'❌ File non trovato: {test_images_path}')
        sys.exit(1)
    
    # Verifica che i file non siano vuoti
    try:
        with open(train_images_path, 'r') as f:
            train_images = json.load(f)
        with open(test_images_path, 'r') as f:
            test_images = json.load(f)
            
        print(f'📊 Dati caricati:')
        print(f'  - Training images: {len(train_images)}')
        print(f'  - Test images: {len(test_images)}')
        
        if len(train_images) == 0:
            print('❌ Dataset di training vuoto!')
            sys.exit(1)
            
        if len(test_images) == 0:
            print('❌ Dataset di test vuoto!')
            sys.exit(1)
            
    except Exception as e:
        print(f'❌ Errore nel caricamento dati JSON: {e}')
        sys.exit(1)
    
    train_loader, test_loader = create_data_loaders(
        config.data_folder,
        config.batch_size,
        workers=0,  # Disabilita multiprocessing per debug
        pin_memory=False,  # Disabilita pin_memory per debug
        train_transform=config.use_transform,
        dataset_format='json',  # Usa formato JSON dato che abbiamo i file JSON
        config=config
    )
    
    print(f'✅ Data loaders creati:')
    print(f'  - Training: {len(train_loader)} batch')
    print(f'  - Test: {len(test_loader)} batch')
    
    # Crea modello
    model, criterion, optimizer = create_model(config)
    
    # Verifica che il modello abbia il metodo detect_objects
    if not hasattr(model, 'detect_objects'):
        print("❌ Errore: il modello non ha il metodo 'detect_objects'")
        print("   Assicurati di usare il modello SSD300 corretto da cnn.py")
        sys.exit(1)
    
    print('✅ Modello verificato con successo')

    # Carica checkpoint se specificato
    start_epoch = 0
    best_loss = float('inf')
    
    if config.resume_checkpoint and os.path.exists(config.resume_checkpoint):
        start_epoch, best_loss = load_checkpoint(config.resume_checkpoint, model, optimizer)
    
    # Solo valutazione
    if args.eval_only:
        print('🔍 Modalità solo valutazione')
        val_loss, mAP, APs = validate_epoch(model, criterion, test_loader, 0, config)
        print(f'Validation Loss: {val_loss:.4f}')
        if mAP is not None:
            print(f'mAP: {mAP:.4f}')
        return
    
    # Training loop
    print('🚀 Inizio training...')
    
    train_losses = []
    val_losses = []
    map_scores = []  # Per tracciare mAP nel tempo
    APs_history = []  # Per salvare la cronologia degli AP per classe
    
    for epoch in range(start_epoch, config.num_epochs):
        # Adatta learning rate
        if epoch in config.decay_lr_at:
            adjust_learning_rate(optimizer, config.decay_lr_to)
        
        # Training
        train_loss = train_epoch(model, criterion, optimizer, train_loader, epoch, config)
        train_losses.append(train_loss)
        
        print(f'\\n📊 Epoca {epoch} completata:')
        print(f'  - Training Loss: {train_loss:.4f}')
        
        # Validazione
        if epoch % config.eval_freq == 0:
            val_loss, mAP, APs = validate_epoch(model, criterion, test_loader, epoch, config)
            val_losses.append(val_loss)
            
            print(f'  - Validation Loss: {val_loss:.4f}')
            
            if mAP is not None:
                map_scores.append(mAP)
                APs_history.append(APs)  # Salva APs per questa epoca
                print(f'  - mAP: {mAP:.4f}')
                
                # Stampa dettagli per classe con mAP > 0.1
                if APs:
                    print('  📈 Top performing classes:')
                    sorted_aps = sorted(APs.items(), key=lambda x: x[1], reverse=True)
                    for class_name, ap in sorted_aps[:5]:  # Top 5 classi
                        if ap > 0.1:
                            print(f'    - {class_name}: {ap:.3f}')
            
            # Salva miglior modello (ora basato su mAP se disponibile, altrimenti su loss)
            is_best = False
            if mAP is not None and map_scores:
                is_best = mAP >= max(map_scores)
                if is_best:
                    best_loss = val_loss
                    print(f'🎉 Nuovo miglior modello! mAP: {mAP:.4f}')
            else:
                is_best = val_loss < best_loss
                if is_best:
                    best_loss = val_loss
                    print(f'🎉 Nuovo miglior modello! Loss: {best_loss:.4f}')
            
            save_checkpoint(epoch, model, optimizer, val_loss, config, is_best)
        else:
            # Riempi con ultimo valore per il plot
            if val_losses:
                val_losses.append(val_losses[-1])
        
        # Salva checkpoint periodico
        if epoch % config.save_freq == 0:
            save_checkpoint(epoch, model, optimizer, train_loss, config)
    
    # Salva stato finale
    save_checkpoint(config.num_epochs - 1, model, optimizer, train_losses[-1], config)
    
    # Plot risultati
    if val_losses:
        plot_training_history(train_losses, val_losses, map_scores, config)
    
    # Salva risultati mAP in JSON
    save_map_results(map_scores, APs_history, config)
    
    print('🎉 Training completato!')
    print(f'💾 Modelli salvati in: {config.checkpoint_folder}')
    print(f'📊 Risultati salvati in: {config.results_folder}')
    
    # Stampa statistiche finali
    if map_scores:
        best_map = max(map_scores)
        print(f'🏆 Miglior mAP raggiunto: {best_map:.4f}')
    
    final_train_loss = train_losses[-1] if train_losses else 0
    final_val_loss = val_losses[-1] if val_losses else 0
    print(f'📈 Loss finale - Training: {final_train_loss:.4f}, Validation: {final_val_loss:.4f}')


if __name__ == '__main__':
    main()
