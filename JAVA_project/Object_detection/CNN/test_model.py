#!/usr/bin/env python3
"""
Script per testare il modello di object detection
Carica il modello addestrato e fa predizioni sulle immagini di test del Dataset 3
"""

import os
import sys
import torch
import torch.nn.functional as F
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path
import argparse

# Aggiungi percorso corrente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cnn import SSD300
from utils_obj import *
import torchvision.transforms.functional as FT

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

class ModelTester:
    def __init__(self, model_path, dataset_path, output_dir="test_predictions"):
        """
        Inizializza il tester del modello
        
        Args:
            model_path: path al modello salvato (.pth)
            dataset_path: path al Dataset_3
            output_dir: directory dove salvare le predizioni
        """
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.test_images_dir = os.path.join(dataset_path, "test", "images")
        self.test_labels_dir = os.path.join(dataset_path, "test", "labels")
        
        # Crea directory output se non exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Carica le classi dal data.yaml
        self.load_classes()
        
        # Carica il modello
        self.load_model()
        
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
        
    def _deduce_n_classes_from_checkpoint(self, state_dict):
        """
        Deduce il numero di classi dalle dimensioni dei layer nel checkpoint
        
        Args:
            state_dict: state dict del modello
            
        Returns:
            numero di classi del modello
        """
        # Per SSD300: cl_conv4_3 ha 4 anchor boxes per cell
        # Dimensione output = n_classes * 4
        if 'pred_convs.cl_conv4_3.weight' in state_dict:
            cl_conv4_3_out_channels = state_dict['pred_convs.cl_conv4_3.weight'].shape[0]
            n_classes = cl_conv4_3_out_channels // 4
            return n_classes
        else:
            print("⚠️  Impossibile dedurre numero classi, usando valore del dataset")
            return self.num_classes
        
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
        
    def visualize_predictions(self, image_path, detections, show_gt=True, save_path=None):
        """
        Visualizza le predizioni su un'immagine

        Args:
            image_path: path all'immagine
            detections: lista delle detections
            show_gt: se mostrare anche le ground truth
            save_path: dove salvare l'immagine (opzionale)
        """
        # Carica immagine originale
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Crea figura
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.imshow(image_rgb)
        
        # Disegna predizioni
        for det in detections:
            bbox = det['bbox']
            x_min, y_min, x_max, y_max = bbox
            width = x_max - x_min
            height = y_max - y_min
            
            # Rettangolo predizione (rosso)
            rect = patches.Rectangle(
                (x_min, y_min), width, height,
                linewidth=2, edgecolor='red', facecolor='none'
            )
            ax.add_patch(rect)
            
            # Etichetta
            label_text = f"{det['class_name']}: {det['confidence']:.2f}"
            ax.text(x_min, y_min - 5, label_text, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.7),
                   fontsize=10, color='white')
        
        # Carica e disegna ground truth se richiesto
        if show_gt:
            gt_boxes = self.load_ground_truth(image_path)
            for gt_box in gt_boxes:
                bbox = gt_box['bbox']
                x_min, y_min, x_max, y_max = bbox
                width = x_max - x_min
                height = y_max - y_min
                
                # Rettangolo ground truth (verde)
                rect = patches.Rectangle(
                    (x_min, y_min), width, height,
                    linewidth=2, edgecolor='green', facecolor='none', linestyle='--'
                )
                ax.add_patch(rect)
                
                # Etichetta GT
                gt_label = f"GT: {gt_box['class_name']}"
                ax.text(x_min, y_max + 5, gt_label,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='green', alpha=0.7),
                       fontsize=10, color='white')
        
        ax.set_title(f"Predizioni - {os.path.basename(image_path)}")
        ax.axis('off')
        
        # Aggiungi legenda
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='red', lw=2, label='Predizioni'),
        ]
        if show_gt:
            legend_elements.append(Line2D([0], [0], color='green', lw=2, linestyle='--', label='Ground Truth'))
        
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"💾 Immagine salvata: {save_path}")
        
        plt.show()
        
    def load_ground_truth(self, image_path):
        """
        Carica le ground truth boxes per un'immagine
        
        Args:
            image_path: path all'immagine
            
        Returns:
            lista delle ground truth boxes
        """
        # Trova il file label corrispondente
        image_name = os.path.basename(image_path)
        label_name = os.path.splitext(image_name)[0] + '.txt'
        label_path = os.path.join(self.test_labels_dir, label_name)
        
        gt_boxes = []
        
        if not os.path.exists(label_path):
            return gt_boxes
            
        # Carica dimensioni immagine
        image = Image.open(image_path)
        img_width, img_height = image.size
        
        # Leggi file label (formato YOLO)
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:5])
                    
                    # Converti da formato YOLO a coordinate assolute
                    x_min = (x_center - width/2) * img_width
                    y_min = (y_center - height/2) * img_height
                    x_max = (x_center + width/2) * img_width
                    y_max = (y_center + height/2) * img_height
                    
                    gt_boxes.append({
                        'bbox': [x_min, y_min, x_max, y_max],
                        'class_id': class_id,
                        'class_name': self.class_names[class_id]
                    })
                    
        return gt_boxes
        
    def test_all_images(self, conf_threshold=0.5, max_images=None):
        """
        Testa il modello su tutte le immagini di test
        
        Args:
            conf_threshold: soglia di confidenza
            max_images: numero massimo di immagini da testare (None = tutte)
        """
        print(f"🎯 Inizio test su tutte le immagini...")
        print(f"📁 Directory immagini: {self.test_images_dir}")
        
        # Lista tutte le immagini
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(Path(self.test_images_dir).glob(f"*{ext}"))
            image_files.extend(Path(self.test_images_dir).glob(f"*{ext.upper()}"))
            
        if max_images:
            image_files = image_files[:max_images]
            
        print(f"📸 Trovate {len(image_files)} immagini da testare")
        
        # Risultati
        all_results = []
        
        for i, image_path in enumerate(image_files):
            print(f"\\n🔍 Processando {i+1}/{len(image_files)}: {image_path.name}")
            
            try:
                # Predizioni
                detections = self.predict_single_image(str(image_path), conf_threshold=conf_threshold)
                
                # Salva risultati
                result = {
                    'image_path': str(image_path),
                    'image_name': image_path.name,
                    'detections': detections,
                    'num_detections': len(detections)
                }
                all_results.append(result)
                
                print(f"  ✅ Trovate {len(detections)} detections")
                
                # Visualizza e salva immagine con predizioni
                save_path = os.path.join(self.output_dir, f"pred_{image_path.name}")
                self.visualize_predictions(str(image_path), detections, save_path=save_path)
                
            except Exception as e:
                print(f"  ❌ Errore processando {image_path.name}: {e}")
                continue
                
        # Salva risultati in JSON
        results_path = os.path.join(self.output_dir, "test_results.json")
        with open(results_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
            
        print(f"\\n📊 Test completato!")
        print(f"💾 Risultati salvati in: {results_path}")
        print(f"🖼️  Immagini salvate in: {self.output_dir}")
        
        # Statistiche
        total_detections = sum(len(r['detections']) for r in all_results)
        avg_detections = total_detections / len(all_results) if all_results else 0
        
        print(f"\\n📈 Statistiche:")
        print(f"  - Immagini processate: {len(all_results)}")
        print(f"  - Detections totali: {total_detections}")
        print(f"  - Detections medie per immagine: {avg_detections:.2f}")
        
        return all_results
        
    def test_single_image_interactive(self, image_name=None):
        """
        Testa una singola immagine in modo interattivo
        
        Args:
            image_name: nome dell'immagine (opzionale)
        """
        """if not image_name:
            # Lista immagini disponibili
            image_files = list(Path(self.test_images_dir).glob("*.jpg"))
            image_files.extend(Path(self.test_images_dir).glob("*.png"))
            
            if not image_files:
                print("❌ Nessuna immagine trovata nella directory test!")
                return
                
            print("📸 Immagini disponibili:")
            for i, img in enumerate(image_files[:10]):  # Mostra prime 10
                print(f"  {i+1}. {img.name}")
                
            if len(image_files) > 10:
                print(f"  ... e altre {len(image_files)-10} immagini")
                
            # Scegli la prima immagine come default
            image_path = str(image_files[0])
            print(f"\\n🎯 Testando: {image_files[0].name}")
        else:
            image_path = os.path.join(self.test_images_dir, image_name)
            if not os.path.exists(image_path):
                print(f"❌ Immagine non trovata: {image_path}")
                return"""
            
        image_path = "/Users/lachithaperera/Documents/AiLab/JAVA_project/Object_detection/victim_view.png"  # For testing purposes
                
        # Fai predizioni
        detections = self.predict_single_image(image_path, conf_threshold=0.5)
        
        # Mostra risultati
        print(f"\\n🎯 Risultati per {os.path.basename(image_path)}:")
        print(f"  📊 Detections trovate: {len(detections)}")
        
        for i, det in enumerate(detections):
            bbox = det['bbox']
            print(f"  {i+1}. {det['class_name']}: {det['confidence']:.3f} "
                  f"[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]")
                  
        # Visualizza
        save_path = os.path.join(self.output_dir, f"single_test_{os.path.basename(image_path)}")
        self.visualize_predictions(image_path, detections, save_path=save_path)
        
        return detections


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(description='Test modello object detection')
    parser.add_argument('--model', default='checkpoints/best_model.pth', 
                       help='Path al modello (.pth)')
    parser.add_argument('--dataset', default='Dataset_3',
                       help='Path al dataset')
    parser.add_argument('--output', default='test_predictions',
                       help='Directory output')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Soglia di confidenza')
    parser.add_argument('--max-images', type=int, default=None,
                       help='Numero massimo di immagini da testare')
    parser.add_argument('--single', type=str, default=None,
                       help='Testa una singola immagine')
    parser.add_argument('--interactive', action='store_true',
                       help='Modalità interattiva per testare una singola immagine')
    
    args = parser.parse_args()
    
    print("🚀 Avvio test modello object detection")
    print(f"📱 Device: {device}")
    print(f"📂 Modello: {args.model}")
    print(f"📁 Dataset: {args.dataset}")
    print(f"💾 Output: {args.output}")
    
    # Verifica che i file esistano
    if not os.path.exists(args.model):
        print(f"❌ Modello non trovato: {args.model}")
        return
        
    if not os.path.exists(args.dataset):
        print(f"❌ Dataset non trovato: {args.dataset}")
        return
        
    # Inizializza tester
    tester = ModelTester(args.model, args.dataset, args.output)
    
    # Esegui test
    if args.single:
        # Test singola immagine
        tester.test_single_image_interactive(args.single)
    elif args.interactive:
        # Modalità interattiva
        tester.test_single_image_interactive()
    else:
        # Test tutte le immagini
        tester.test_all_images(conf_threshold=args.conf, max_images=args.max_images)


if __name__ == "__main__":
    main()