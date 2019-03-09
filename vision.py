# Install Anaconda 4.4.10 (>> conda info)
# pip install google-api-python-client
# pip install google-cloud-storage
# pip install google-auth-httplib2
# pip install PyPDF2
# Steps
# 0. Create Google Account acounts.google.com
# 1. Create GCP project - console.cloud.google.com, instructions at https://cloud.google.com/resource-manager/docs/creating-managing-projects
# 2. Create service account for project and save json key - https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python
# 3. Enable Vision API, Storage API for project - https://console.cloud.google.com/apis/library?project=form-processing
# 4. Create storage bucket matching variable name CROPPED_JPEG_BUCKET_NAME (ensure service account has permissions to modify
# Google vision api documentation - https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.cloud import storage
from wand.image import Image
import os
from PyPDF2 import PdfFileReader


#Required Scopes to for GCP storage and vision api
SCOPES = ['https://www.googleapis.com/auth/cloud-platform'
    ,'https://www.googleapis.com/auth/cloud-vision']
#service account credentials
SERVICE_ACCOUNT_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__)
                                                , 'creds'
                                                , 'sa-505-at-form-processing_iam_gserviceaccount_com.json')

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_CREDENTIALS_PATH, scopes=SCOPES)
#specifiy GCS bucket name to upload image file to and read using vision api
CROPPED_JPEG_BUCKET_NAME = 'jpeg-cropped-address'
#secifiy the incoming directory which holds the PDF files
INCOMING_DIR = 'pdf-incoming'
PROCESSED_DIR = 'pdf-processed'
CROPPED_JPEG_DIR = 'jpeg_address_block'
ERROR_DIR = 'pdf-error'
TEXT_DIR = 'address_text_read'

# Can only use API developer key with publicly accessable files
#APIKEY="AIzaSyAi5cDB-YrDmLf5c6vV8tYBIwvELMu_UeY"

#create authenticated google service objects
service = build('vision', 'v1', credentials=credentials)
google_storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_CREDENTIALS_PATH)
#configure working bucket
cropped_jpeg_bucket = google_storage_client.get_bucket(CROPPED_JPEG_BUCKET_NAME)

def isFileTypePDF(filename):
    '''
    Checks whether filename is a pdf type or not by trying to open it and checking the number of pages.
    File extension does not play into it.
    :param filename: filename and relative path
    :return: true/false
    '''
    try:
        doc = PdfFileReader(open(filename, "rb"))
        num_pages = doc.numPages
        return True
    except:
        return False


#process PDF files in incoming directory
pdf_files = os.listdir(os.path.join(os.curdir,INCOMING_DIR))
for pdf_file in pdf_files:
    if isFileTypePDF("%s/%s"%(os.path.join(os.curdir,INCOMING_DIR),pdf_file)):

        #Convert the first page of PDF scan to jpeg and crop the image to the address block
        image_pdf = Image(filename=("%s/%s[0]"%(os.path.join(os.curdir,INCOMING_DIR),pdf_file)), resolution=300)
        image_jpeg = image_pdf.convert('jpeg')
        image_jpeg_cropped = image_jpeg.crop(200,600,1100,1000)
        image_jpeg.save(filename=("%s/%s.jpeg"%(os.path.join(os.curdir,CROPPED_JPEG_DIR),pdf_file)))
        # upload cropped image to Google Cloud Storage
        blob = cropped_jpeg_bucket.blob('%s.jpeg'%pdf_file)
        blob.upload_from_filename("%s/%s.jpeg"%(os.path.join(os.curdir,CROPPED_JPEG_DIR),pdf_file))
        # Read text from image (uploaded cropped JPEG)
        IMAGE=("gs://%s/%s.jpeg"%(CROPPED_JPEG_BUCKET_NAME,pdf_file))
        request = service.images().annotate(body={
                'requests': [{
                        'image': {
                            'source': {
                                'gcs_image_uri': IMAGE
                            }
                        },
                        'features': [{
                            'type': 'TEXT_DETECTION',
                            'maxResults': 3,
                        }]
                    }],
                })
        responses = request.execute(num_retries=3)
        output_filename = ("%s/%s.txt"%(os.path.join(os.curdir,TEXT_DIR),pdf_file))
        output_file = open(output_filename,"w")
        output_file.write(responses['responses'][0]['textAnnotations'][0]['description'])
        output_file.close

        #clean up GCS
        blob.delete()
        #move original file to processed directory
        os.rename(("%s/%s"%(os.path.join(os.curdir,INCOMING_DIR),pdf_file))
                   , ("%s/%s"%(os.path.join(os.curdir,PROCESSED_DIR),pdf_file)))

    else:
        print('%s is not of file type PDF.  Moved to %s directory to prevent processing again.  Verify file.'%(pdf_file,ERROR_DIR))
        os.rename(("%s/%s"%(os.path.join(os.curdir,INCOMING_DIR),pdf_file))
                   , ("%s/%s"%(os.path.join(os.curdir,ERROR_DIR),pdf_file)))