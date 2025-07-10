import torch
from  torch.utils.data  import Dataset
import json
import os
from PIL import Image, ImageDraw
import cv2
import numpy as np
import yaml
import glob
from utils_obj import transform, label_map, rev_label_map
from augmentation import advanced_transform, get_augmentation_stats

class CustomDataset(Dataset):
    """
    Dataset personalizzato per object detection usando SSD
    Supporta sia formato JSON che formato YOLO-like
    """
    
    def __init__(self, data_folder, split, transform=None, dataset_format='json', config=None):
        """
        :param data_folder: cartella contenente i dati
        :param split: 'TRAIN' o 'TEST' per formato JSON, 'train' o 'valid' per formato YOLO
        :param transform: transform da applicare alle immagini
        :param dataset_format: 'json' per formato originale, 'yolo' per Dataset_4
        :param config: configurazione con parametri di augmentation
        """
        self.split = split
        self.data_folder = data_folder
        self.transform = transform
        self.dataset_format = dataset_format.lower()
        self.config = config
        
        if self.dataset_format == 'json':
            self._load_json_format()
        elif self.dataset_format == 'yolo':
            self._load_yolo_format()
        else:
            raise ValueError(f"Formato dataset non supportato: {dataset_format}")
        
        # Debug: controlla che le immagini siano state caricate
        if not hasattr(self, 'images') or len(self.images) == 0:
            raise ValueError(f"Nessuna immagine caricata per split '{split}' formato '{dataset_format}'")
        
        print(f"✅ Dataset caricato: {len(self.images)} immagini per split '{split}'")
            
    def _load_json_format(self):
        """Carica dataset in formato JSON originale"""
        self.split = self.split.upper()
        assert self.split in {'TRAIN', 'TEST'}
        
        images_file = os.path.join(self.data_folder, self.split + '_images.json')
        objects_file = os.path.join(self.data_folder, self.split + '_objects.json')
        
        print(f"🔍 Caricamento formato JSON per split '{self.split}':")
        print(f"  - Images file: {images_file}")
        print(f"  - Objects file: {objects_file}")
        
        if not os.path.exists(images_file):
            raise FileNotFoundError(f"File immagini non trovato: {images_file}")
        if not os.path.exists(objects_file):
            raise FileNotFoundError(f"File oggetti non trovato: {objects_file}")
        
        # Carica dati JSON
        with open(images_file, 'r') as j:
            self.images = json.load(j)
        with open(objects_file, 'r') as j:
            self.objects = json.load(j)
            
        print(f"  - Caricate {len(self.images)} immagini")
        print(f"  - Caricati {len(self.objects)} oggetti")
        
        if len(self.images) == 0:
            raise ValueError(f"Nessuna immagine trovata nel file {images_file}")
        
        assert len(self.images) == len(self.objects)
        print(f'✅ Dataset JSON {self.split}: {len(self.images)} immagini caricate.')
    
    def _load_yolo_format(self):
        """Carica dataset in formato YOLO-like (Dataset_4)"""
        self.split = self.split.lower()
        assert self.split in {'train', 'valid'}
        
        # Carica configurazione classi
        yaml_path = os.path.join(self.data_folder, 'data.yaml')
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            self.class_names = config['names']
            self.num_classes = config['nc']
        else:
            # Classi di default se non esiste data.yaml
            self.class_names = ['Back', 'Hide', 'Interaction', 'Jason', 'Obstacle', 'Slow', 'Victim', 'Win']
            self.num_classes = len(self.class_names)
        
        # Trova tutte le immagini
        images_dir = os.path.join(self.data_folder, self.split, 'images')
        labels_dir = os.path.join(self.data_folder, self.split, 'labels')
        
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        self.images = []
        for ext in image_extensions:
            self.images.extend(glob.glob(os.path.join(images_dir, ext)))
        
        self.images.sort()
        
        # Crea lista degli oggetti corrispondenti
        self.objects = []
        for img_path in self.images:
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            label_path = os.path.join(labels_dir, base_name + '.txt')
            
            if os.path.exists(label_path):
                objects_dict = self._parse_yolo_label(label_path, img_path)
            else:
                # Se non esiste il file label, crea oggetto vuoto
                objects_dict = {'boxes': [], 'labels': [], 'difficulties': []}
            
            self.objects.append(objects_dict)
        
        print(f'Dataset YOLO {self.split}: {len(self.images)} immagini caricate.')
    
    def _parse_yolo_label(self, label_path, img_path):
        """Parsifica un file label YOLO-like"""
        # Leggi dimensioni immagine
        image = Image.open(img_path)
        img_width, img_height = image.size
        
        boxes = []
        labels = []
        difficulties = []
        
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x1 = float(parts[1])
                    y1 = float(parts[2])
                    x2 = float(parts[3])
                    y2 = float(parts[4])
                    
                    # Converti coordinate assolute in frazionali (0-1)
                    x1_norm = x1 / img_width
                    y1_norm = y1 / img_height
                    x2_norm = x2 / img_width
                    y2_norm = y2 / img_height
                    
                    # Assicurati che le coordinate siano nell'ordine corretto
                    x1_norm, x2_norm = min(x1_norm, x2_norm), max(x1_norm, x2_norm)
                    y1_norm, y2_norm = min(y1_norm, y2_norm), max(y1_norm, y2_norm)
                    
                    # Limita le coordinate a [0, 1]
                    x1_norm = max(0, min(1, x1_norm))
                    y1_norm = max(0, min(1, y1_norm))
                    x2_norm = max(0, min(1, x2_norm))
                    y2_norm = max(0, min(1, y2_norm))
                    
                    boxes.append([x1_norm, y1_norm, x2_norm, y2_norm])
                    labels.append(class_id + 1)  # +1 perché il background è classe 0
                    difficulties.append(0)  # Nessuna difficoltà specificata
        
        return {
            'boxes': boxes,
            'labels': labels,
            'difficulties': difficulties
        }
    
    def __getitem__(self, i):
        # Leggi immagine
        image = Image.open(self.images[i], mode='r')
        image = image.convert('RGB')
        
        # Leggi oggetti
        objects = self.objects[i]
        
        if self.dataset_format == 'json':
            boxes = torch.FloatTensor(objects['boxes'])  # (n_objects, 4)
            labels = torch.LongTensor(objects['labels'])  # (n_objects)
            difficulties = torch.ByteTensor(objects['difficulties'])  # (n_objects)
        else:  # formato yolo
            if len(objects['boxes']) > 0:
                boxes = torch.FloatTensor(objects['boxes'])  # (n_objects, 4)
                labels = torch.LongTensor(objects['labels'])  # (n_objects)
                difficulties = torch.ByteTensor(objects['difficulties'])  # (n_objects)
            else:
                # Se non ci sono oggetti, crea tensori vuoti
                boxes = torch.FloatTensor([])  # (0, 4)
                labels = torch.LongTensor([])  # (0)
                difficulties = torch.ByteTensor([])  # (0)
        
        # Applica trasformazioni
        if self.transform:
            # Usa advanced_transform se config è disponibile e advanced_augmentation è True
            if (self.config and 
                hasattr(self.config, 'advanced_augmentation') and 
                self.config.advanced_augmentation):
                # Logging per confermare l'uso della data augmentation avanzata
                if i % 50 == 0:  # Log ogni 50 immagini per non sovraccaricare
                    print(f"🔄 Applicando data augmentation avanzata su immagine {i} ({os.path.basename(self.images[i])})")
                image, boxes, labels, difficulties = advanced_transform(
                    image, boxes, labels, difficulties, self.split, self.config
                )
            else:
                # Usa la transform standard
                if i % 50 == 0:
                    print(f"📷 Applicando transform standard su immagine {i} ({os.path.basename(self.images[i])})")
                image, boxes, labels, difficulties = self.transform(
                    image, boxes, labels, difficulties, self.split
                )
        
        return image, boxes, labels, difficulties
    
    def __len__(self):
        return len(self.images)
    
    def collate_fn(self, batch):
        """
        Collate function personalizzata per gestire batch con numero diverso di oggetti
        """
        images = []
        boxes = []
        labels = []
        difficulties = []
        
        for b in batch:
            images.append(b[0])
            boxes.append(b[1])
            labels.append(b[2])
            difficulties.append(b[3])
        
        images = torch.stack(images, dim=0)
        
        return images, boxes, labels, difficulties


def create_data_loaders(data_folder, batch_size, workers, pin_memory, train_transform=True, dataset_format='json', config=None):
    """
    Crea DataLoader per training e testing
    
    :param data_folder: cartella contenente i dati
    :param batch_size: dimensione del batch
    :param workers: numero di worker per il DataLoader
    :param pin_memory: se usare pin_memory
    :param train_transform: se applicare trasformazioni
    :param dataset_format: 'json' per formato originale, 'yolo' per Dataset_4
    :param config: configurazione con parametri di augmentation
    """
    
    if dataset_format.lower() == 'json':
        train_split = 'TRAIN'
        test_split = 'TEST'
    else:  # formato yolo
        train_split = 'train'
        test_split = 'valid'
    
    # Training dataset
    train_dataset = CustomDataset(data_folder, 
                                split=train_split,
                                transform=transform if train_transform else None,
                                dataset_format=dataset_format,
                                config=config)
    
    # Verifica che il dataset di training non sia vuoto
    if len(train_dataset) == 0:
        raise ValueError(f"Dataset di training vuoto! Verifica i dati in {data_folder}")
    
    print(f'✅ Train dataset creato: {len(train_dataset)} campioni')
    train_loader = torch.utils.data.DataLoader(train_dataset, 
                                             batch_size=batch_size,
                                             shuffle=True,
                                             collate_fn=train_dataset.collate_fn,
                                             num_workers=workers,
                                             pin_memory=pin_memory)
    
    # Test dataset
    test_dataset = CustomDataset(data_folder,
                               split=test_split, 
                               transform=transform if train_transform else None,
                               dataset_format=dataset_format,
                               config=config)
    
    # Verifica che il dataset di test non sia vuoto
    if len(test_dataset) == 0:
        raise ValueError(f"Dataset di test vuoto! Verifica i dati in {data_folder}")
    
    print(f'✅ Test dataset creato: {len(test_dataset)} campioni')
    
    test_loader = torch.utils.data.DataLoader(test_dataset,
                                             batch_size=batch_size,
                                             shuffle=False,
                                             collate_fn=test_dataset.collate_fn,
                                             num_workers=workers,
                                             pin_memory=pin_memory)
    
    return train_loader, test_loader


def show_sample_batch(data_loader, n_samples=4):
    """
    Mostra un batch di esempio dal dataset
    """
    # Ottieni un batch
    data_iter = iter(data_loader)
    images, boxes_list, labels_list, difficulties_list = next(data_iter)
    
    # Parametri per de-normalizzazione
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()
    
    for i in range(min(n_samples, len(images))):
        # De-normalizza l'immagine
        img_tensor = images[i].clone()
        for t, m, s in zip(img_tensor, mean, std):
            t.mul_(s).add_(m)
        img_tensor = torch.clamp(img_tensor, 0, 1)
        
        # Converti in numpy per visualizzazione
        img_np = img_tensor.permute(1, 2, 0).numpy()
        
        axes[i].imshow(img_np)
        axes[i].set_title(f'Immagine {i+1} - {len(boxes_list[i])} oggetti')
        
        # Disegna bounding box
        if len(boxes_list[i]) > 0:
            boxes = boxes_list[i]
            labels = labels_list[i]
            
            # Le coordinate sono in formato frazionale (0-1)
            h, w = img_np.shape[:2]
            
            for j in range(len(boxes)):
                box = boxes[j]
                label = labels[j].item()
                
                # Converti coordinate frazionali in pixel
                x1 = box[0].item() * w
                y1 = box[1].item() * h
                x2 = box[2].item() * w
                y2 = box[3].item() * h
                
                # Disegna rettangolo
                rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                       linewidth=2, edgecolor='red', facecolor='none')
                axes[i].add_patch(rect)
                
                # Aggiungi etichetta
                if label in rev_label_map:
                    class_name = rev_label_map[label]
                    axes[i].text(x1, y1-5, class_name, 
                               color='red', fontsize=10, fontweight='bold')
        
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    print(f'Batch shape: {images.shape}')
    print(f'Numero di oggetti per immagine: {[len(boxes) for boxes in boxes_list]}')
    print(f'Etichette: {[labels.tolist() for labels in labels_list]}')


def test_yolo_dataset(data_folder, split='train'):
    """
    Funzione di test per verificare il caricamento del dataset YOLO
    """
    dataset = CustomDataset(data_folder, split=split, dataset_format='yolo')
    
    print(f"Dataset caricato: {len(dataset)} immagini")
    print(f"Classi disponibili: {dataset.class_names}")
    
    # Testa il primo elemento
    if len(dataset) > 0:
        image, boxes, labels, difficulties = dataset[0]
        print(f"Prima immagine:")
        print(f"  - Dimensioni immagine: {image.size}")
        print(f"  - Numero di oggetti: {len(boxes)}")
        print(f"  - Etichette: {labels.tolist()}")
        print(f"  - Bounding boxes: {boxes.tolist()}")
    
    return dataset


# Esempio di utilizzo:
if __name__ == "__main__":
    # Test del dataset YOLO
    yolo_dataset_path = "/Users/lachithaperera/Documents/AiLab/JAVA_project/Object_detection/CNN/Dataset_4"
    
    if os.path.exists(yolo_dataset_path):
        print("Test del dataset YOLO:")
        test_dataset = test_yolo_dataset(yolo_dataset_path, 'train')
        
        # Crea data loader
        train_loader, test_loader = create_data_loaders(
            yolo_dataset_path, 
            batch_size=4, 
            workers=0, 
            pin_memory=False,
            dataset_format='yolo'
        )
        
        print(f"Train loader: {len(train_loader)} batch")
        print(f"Test loader: {len(test_loader)} batch")
    else:
        print("Dataset YOLO non trovato")
