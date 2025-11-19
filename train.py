from ultralytics import YOLO

model = YOLO('yolov8n.pt') 
DATASET_PATH = './YOLO/data.yaml' 

results = model.train(
    data=DATASET_PATH, 
    epochs=50, 
    imgsz=640, 
    name='stop_detector'
)

print("Обучение завершено!")

