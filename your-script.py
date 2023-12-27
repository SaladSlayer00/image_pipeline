import boto3
import os
from datasets import load_dataset, load_metric, Image, DatasetDict, Dataset, load_from_disk, 
from huggingface_hub import HfApi, Repository

hf_token = os.environ.get('HUGGINGFACE_HUB_TOKEN')
if hf_token:
    HfFolder.save_token(hf_token)  # This will save the token for later use by Hugging Face libraries
else:
    raise ValueError("Hugging Face token not found. Make sure it is passed as an environment variable.")

def download_images(bucket_name):
    s3 = boto3.client('s3')
    print(f"Connecting to bucket: {bucket_name}")
    response = s3.list_objects_v2(Bucket=bucket_name)

    directory_created = False
    local_directory = ""

    if 'Contents' in response:
        print(f"Found {len(response['Contents'])} objects in bucket.")
        for obj in response['Contents']:
            print(f"Checking object: {obj['Key']}")
            if obj['Key'].endswith('.jpg') or obj['Key'].endswith('.png'):  # Add more image formats if needed
                print(f"Found image: {obj['Key']}")
                if not directory_created:
                    # Extract the file name without the extension
                    image_name = os.path.splitext(obj['Key'])[0]
                    local_directory = image_name
                    if not os.path.exists(local_directory):
                        print(f"Creating directory: {local_directory}")
                        os.makedirs(local_directory)
                    directory_created = True

                # Download the file
                print(f"Downloading image to {local_directory}/{obj['Key']}")
                s3.download_file(bucket_name, obj['Key'], os.path.join(local_directory, obj['Key']))
    else:
        print("No contents found in bucket.")

# Replace 'your-bucket-name' with your actual S3 bucket name
download_images('imagefilessml')

import shutil
import random

def split_train_test(image_dir, train_ratio=0.7):
    # Make sure the train and test directories exist
    train_dir = os.path.join(image_dir, 'train')
    test_dir = os.path.join(image_dir, 'test')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # Get all image filenames
    all_images = [f for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')]

    # Shuffle the list for random split
    random.shuffle(all_images)

    # Calculate the split index
    split_index = int(len(all_images) * train_ratio)

    # Split the images
    train_images = all_images[:split_index]
    test_images = all_images[split_index:]

    # Move the images to the respective directories
    for image in train_images:
        shutil.move(os.path.join(image_dir, image), train_dir)
    
    for image in test_images:
        shutil.move(os.path.join(image_dir, image), test_dir)
        
    return train_dir, test_dir

# Call the function
train_dir, test_dir = split_train_test(local_directory)  # Replace local_directory with the directory where images are downloaded


# Function to create the dataset
def create_dataset(image_dir):
    # Store the data in this dictionary
    data = {'image': [], 'label': []}

    # List the directories in the image_dir
    for label in os.listdir(image_dir):
        # Skip hidden directories or files
        if label.startswith('.'):
            continue

        class_dir = os.path.join(image_dir, label)

        # Ensure it's a directory
        if not os.path.isdir(class_dir):
            continue

        # List the images in the class_dir
        for image_name in os.listdir(class_dir):
            # Skip hidden files
            if image_name.startswith('.'):
                continue

            # Get the image path
            image_path = os.path.join(class_dir, image_name)
            # Add the image and label to the data dictionary
            data['image'].append(image_path)
            data['label'].append(label)

    # Create a dataset from the data dictionary
    dataset = Dataset.from_dict(data)
    # Cast the 'image' column to the Image feature type
    dataset = dataset.cast_column('image', Image())
    return dataset

# Create the datasets
train_dataset = create_dataset(train_dir)
test_dataset = create_dataset(test_dir)

# Create a DatasetDict
dataset_dict = DatasetDict({
    'train': train_dataset,
    'test': test_dataset
})


# After creating the dataset, you can save it with
dataset_dict.push_to_hub('SaladSlayer00/twin_matcher')

