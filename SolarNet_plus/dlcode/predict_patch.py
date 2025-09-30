import torch
import numpy as np
import os
import argparse
from torch.utils.data import Dataset, DataLoader
from PIL import Image, UnidentifiedImageError
import cv2
from SolarNet import SolarNet

class generateDataset(Dataset):
    def __init__(self, dirFiles, img_size, colordim):
        self.dirFiles = dirFiles
        image_extensions = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
        self.nameFiles = [name for name in os.listdir(dirFiles) if name.lower().endswith(image_extensions) and os.path.isfile(os.path.join(dirFiles, name))]
        self.numFiles = len(self.nameFiles)
        self.img_size = img_size
        print(f"Found {self.numFiles} image(s) to predict.")

    def __getitem__(self, index):
        filename = os.path.join(self.dirFiles, self.nameFiles[index])
        try:
            img = Image.open(filename).convert('RGB')
        except (IOError, UnidentifiedImageError):
            print(f"Warning: Skipping corrupted or non-image file: {filename}")
            return None, None

        from torchvision import transforms
        preprocess = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        img_tensor = preprocess(img)
        imgName, _ = os.path.splitext(self.nameFiles[index])
        return img_tensor, imgName
    
    def __len__(self):
        return self.numFiles

def collate_fn(batch):
    batch = list(filter(lambda x: x[0] is not None, batch))
    return torch.utils.data.dataloader.default_collate(batch) if batch else (None, None)

def main(args):
    device = torch.device("cuda" if args.cuda and torch.cuda.is_available() else "cpu")
    print(f"===> Using device for prediction: {device}")
    model = SolarNet(in_channels=args.colordim, n_class=args.num_class).to(device)
    model.load_state_dict(torch.load(args.pretrain_net, map_location=device))
    model.eval()
    predDataset = generateDataset(args.pre_root_dir, args.img_size, args.colordim)
    predLoader = DataLoader(dataset=predDataset, batch_size=args.predictbatchsize, num_workers=args.threads, collate_fn=collate_fn)
    with torch.no_grad():
        for batch_x, batch_name in predLoader:
            if batch_x is None: continue
            batch_x = batch_x.to(device)
            out = model(batch_x)
            pred_label2 = torch.argmax(out[1], 1).cpu().numpy()
            pred_label3 = torch.argmax(out[2], 1).cpu().numpy()
            for i in range(len(batch_name)):
                cv2.imwrite(os.path.join(args.preDir2, f"{batch_name[i]}.png"), pred_label2[i].astype(np.uint8))
                cv2.imwrite(os.path.join(args.preDir3, f"{batch_name[i]}.png"), pred_label3[i].astype(np.uint8))
                print(f"Processed and saved maps for: {batch_name[i]}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cuda', action='store_true', default=True)
    parser.add_argument('--predictbatchsize', type=int, default=1)
    parser.add_argument('--threads', type=int, default=0)
    parser.add_argument('--img_size', type=int, default=512)
    parser.add_argument('--colordim', type=int, default=3)
    parser.add_argument('--pretrain_net', required=True)
    parser.add_argument('--pre_root_dir', required=True)
    parser.add_argument('--num_class', type=int, default=9)
    parser.add_argument('--preDir2', required=True)
    parser.add_argument('--preDir3', required=True)
    args = parser.parse_args()
    os.makedirs(args.preDir2, exist_ok=True)
    os.makedirs(args.preDir3, exist_ok=True)
    main(args)