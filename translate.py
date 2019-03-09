APIKEY="AIzaSyAESgUkyD6-JXfyvyIvDaIev2Cb9I-l_Hs"

from googleapiclient.discovery import build
service = build('translate', 'v2', developerKey=APIKEY)

# use the service
inputs = ['is it really this easy?', 'amazing technology', 'wow']
outputs = service.translations().list(source='en', target='fr', q=inputs).execute()
# print outputs
for input, output in zip(inputs, outputs['translations']):
  print u"{0} -> {1}".format(input, output['translatedText'])

print '--------------------------------------------------------'
foreignlang = 'zh'
foreignText = '请您爱护和保\n护卫生创建优\n美水环境'

inputs=[foreignText]
outputs = service.translations().list(source=foreignlang, target='en', q=inputs).execute()
# print outputs
for input, output in zip(inputs, outputs['translations']):
  print u"{0} -> {1}".format(input, output['translatedText'])