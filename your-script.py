import boto3
import os

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


