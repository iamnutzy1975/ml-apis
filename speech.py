APIKEY="AIzaSyAESgUkyD6-JXfyvyIvDaIev2Cb9I-l_Hs"

from googleapiclient.discovery import build
sservice = build('speech', 'v1beta1', developerKey=APIKEY)
response = sservice.speech().syncrecognize(
    body={
        'config': {
            'encoding': 'LINEAR16',
            'sampleRate': 16000
        },
        'audio': {
            'uri': 'gs://cloud-training-demos/vision/audio.raw'
            }
        }).execute()
print response