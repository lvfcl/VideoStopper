from ultralytics import YOLO

model = YOLO('yolov8s.pt') 
DATASET_PATH = './YOLO/data.yaml' 

results = model.train(
    data=DATASET_PATH, 
    epochs=300, 
    patience=0,
    imgsz=640, 
    name='stop_detector'
)

print("Training completed!")

