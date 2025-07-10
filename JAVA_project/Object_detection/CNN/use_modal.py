import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import json
import os
from cnn import SSD300
from utils_obj import *

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("[TRAIN] Device set to: Apple Silicon GPU (mps)")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("[TRAIN] Device set to: CUDA GPU")
else:
    device = torch.device("cpu")
    print("[TRAIN] Device set to: CPU")

def transform_for_inference(image):
    """
    Trasformazione per inferenza (solo immagine, senza bounding box)
    
    Args:
        image: PIL Image
        
    Returns:
        tensor dell'immagine trasformata
    """
    # Parametri di normalizzazione ImageNet (come nel training)
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    
    # Ridimensiona a 300x300 (dimensione richiesta da SSD300)
    new_image = image.resize((300, 300))
    
    # Converti in tensor
    new_image = FT.to_tensor(new_image)
    
    # Normalizza
    new_image = FT.normalize(new_image, mean=mean, std=std)
    
    return new_image

class ObjectDetector:
    def __init__(self, model_path, dataset_path):
        self.model_path = model_path
        self.dataset_path = dataset_path

        # Carica le classi dal data.yaml
        self.load_classes()
        
        # Carica il modello
        self.load_model()
        pass

    def load_classes(self):
        """Carica le classi dal file data.yaml"""
        import yaml
        yaml_path = os.path.join(self.dataset_path, "data.yaml")
        
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            
        self.class_names = data['names']
        self.num_classes = data['nc']
        print(f"📋 Classi caricate: {self.class_names}")

    def load_model(self):
        """Carica il modello addestrato"""
        print(f"🔄 Caricamento modello da {self.model_path}...")
        
        # Carica il checkpoint per analizzare le dimensioni
        checkpoint = torch.load(self.model_path, map_location=device, weights_only=False)
        
        # Estrae lo state_dict
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
            
        # Deduce il numero di classi dalle dimensioni del modello salvato
        model_n_classes = self._deduce_n_classes_from_checkpoint(state_dict)
        
        if model_n_classes != self.num_classes:
            print(f"⚠️  Mismatch numero classi:")
            print(f"   Dataset: {self.num_classes} classi")
            print(f"   Modello: {model_n_classes} classi")
            print(f"   Usando il numero di classi del modello: {model_n_classes}")
            self.model_n_classes = model_n_classes
        else:
            self.model_n_classes = self.num_classes
        
        # Crea il modello SSD300 con il numero corretto di classi
        self.model = SSD300(n_classes=self.model_n_classes)
        
        # Carica i pesi del modello
        self.model.load_state_dict(state_dict)
            
        self.model = self.model.to(device)
        self.model.eval()
        
        print(f"✅ Modello caricato con successo!")
        print(f"   Classi modello: {self.model_n_classes}")

    def preprocess_image(self, image_path):
        """
        Preprocessa un'immagine per l'inferenza
        
        Args:
            image_path: path all'immagine
            
        Returns:
            tensor dell'immagine preprocessata e dimensioni originali
        """
        # Carica immagine
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        
        # Applica la trasformazione per inferenza
        image_tensor = transform_for_inference(image)
        
        return image_tensor.unsqueeze(0).to(device), original_size
        
    def postprocess_predictions(self, predictions, original_size, conf_threshold=0.5):
        """
        Post-processa le predizioni del modello
        
        Args:
            predictions: output del detect_objects (boxes, labels, scores)
            original_size: dimensioni originali dell'immagine
            conf_threshold: soglia di confidenza (già applicata da detect_objects)
            
        Returns:
            lista di detections filtrate
        """
        boxes, labels, scores = predictions
        
        # Le coordinate sono già in formato fractional (0-1), scale alle dimensioni originali
        if len(boxes) > 0:
            boxes[:, [0, 2]] *= original_size[0]  # x_min, x_max
            boxes[:, [1, 3]] *= original_size[1]  # y_min, y_max
        
        detections = []
        for i in range(len(boxes)):
            label_idx = labels[i].item()
            
            # Gestisce il mismatch tra numero classi del modello e dataset
            if hasattr(self, 'model_n_classes') and self.model_n_classes != self.num_classes:
                # Se il modello ha più classi del dataset, mappa l'indice
                if label_idx > 0 and label_idx <= len(self.class_names):
                    class_name = self.class_names[label_idx - 1]  # -1 perché background è 0
                else:
                    class_name = f"class_{label_idx}"  # Classe sconosciuta
            else:
                # Mappatura normale
                class_name = self.class_names[label_idx - 1] if label_idx > 0 else "background"
            
            detections.append({
                'bbox': boxes[i].cpu().numpy(),
                'label': label_idx,
                'class_name': class_name,
                'confidence': scores[i].item()
            })
            
        return detections

    def predict_single_image(self, image_path, conf_threshold=0.5):
        """
        Fa predizioni su una singola immagine
        
        Args:
            image_path: path all'immagine
            conf_threshold: soglia di confidenza per le detection
            
        Returns:
            detections predette
        """
        # Preprocessa immagine
        image_tensor, original_size = self.preprocess_image(image_path)
        
        # Inferenza
        with torch.no_grad():
            # Il modello restituisce locations e scores
            predicted_locs, predicted_scores = self.model(image_tensor)
            
            # Usa la funzione detect_objects del modello per fare NMS e filtraggio
            det_boxes, det_labels, det_scores = self.model.detect_objects(
                predicted_locs, predicted_scores, 
                min_score=conf_threshold, 
                max_overlap=0.45, 
                top_k=200
            )
            
            # Estrae risultati per la prima (e unica) immagine del batch
            boxes = det_boxes[0]
            labels = det_labels[0] 
            scores = det_scores[0]
            
        # Post-processing
        detections = self.postprocess_predictions(
            (boxes, labels, scores), original_size, conf_threshold=0.0  # Già filtrato da detect_objects
        )
        
        return detections