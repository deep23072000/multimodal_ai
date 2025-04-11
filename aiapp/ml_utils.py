# aiapp/ml_utils.py

import torch
from torchvision.models import convnext_base, ConvNeXt_Base_Weights
import torchvision.transforms as transforms
from PIL import Image
import os

# Load model and labels once (global)
weights = ConvNeXt_Base_Weights.DEFAULT
model = convnext_base(weights=weights)
model.eval()
transform = weights.transforms()

# Load labels
labels_path = os.path.join(os.path.dirname(__file__), "imagenet_classes.txt")
if not os.path.exists(labels_path):
    import requests
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    response = requests.get(url)
    with open(labels_path, "w") as f:
        f.write(response.text)

with open(labels_path) as f:
    labels = [line.strip() for line in f.readlines()]

def classify_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        img_t = transform(image)
        batch_t = torch.unsqueeze(img_t, 0)

        with torch.no_grad():
            output = model(batch_t)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            top3_prob, top3_indices = torch.topk(probabilities, 3)

        predictions = []
        for i in range(3):
            label = labels[top3_indices[i]]
            prob = top3_prob[i].item()
            predictions.append((label, prob))
        return predictions

    except Exception as e:
        return [("Error processing image", 0.0)]
