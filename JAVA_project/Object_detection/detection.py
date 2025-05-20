import json
from ultralytics import YOLO


INPUT_PATH = ["jason_view.png", "victim_view.png"]
OUTPUT_PATH = ["detections_jason.json", "detections_panam.json"]


def object_detection():
    # Carica il modello YOLO addestrato
    model = YOLO("object_detection/best.pt")

    i = 0
    for path in INPUT_PATH:
        results = model(path)

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
        with open(OUTPUT_PATH[i], "w") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Detections salvate in {OUTPUT_PATH[i]}")
        i += 1


if __name__ == "__main__":
    while True:
        object_detection()
