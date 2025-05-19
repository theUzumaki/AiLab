import json
from ultralytics import YOLO
import sys


def object_detection(kind):
    # Carica il modello YOLO addestrato
    model = YOLO("Object_detection/best.pt")

    # Inferenzia sullo screenshot del gioco
    if kind == "jason":
        results = model("jason_view.png")
    else:
        results = model("victim_view.png")

    # Estrai i bounding box rilevati
    output = []
    for r in results:
        for box in r.boxes:
            cls = r.names[int(box.cls)]
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            output.append(
                {
                    "class": cls,  # "killer" o "victim"
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf[0]),
                }
            )

    # Salva in formato JSO
    if kind == "jason":
        with open("detections_jason.json", "w") as f:
            json.dump(output, f, indent=2)
    else:
        with open("detections_panam.json", "w") as f:
            json.dump(output, f, indent=2)

    print("✅ Detections salvate in detections.json")


if __name__ == "__main__":
    object_detection(sys.argv[1])
