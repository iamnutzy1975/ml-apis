APIKEY="AIzaSyAESgUkyD6-JXfyvyIvDaIev2Cb9I-l_Hs"

from googleapiclient.discovery import build

lservice = build('language', 'v1beta1', developerKey=APIKEY)
quotes = [
  'To succeed, you must have tremendous perseverance, tremendous will.',
  'It is not that I am so smart, it is just that I stay with problems longer.',
  'Love is quivering happiness.',
  'Love is of all passions the strongest, for it attacks simultaneously the head, the heart, and the senses.',
  'What difference does it make to the dead, the orphans and the homeless, whether the mad destruction is wrought under the name of totalitarianism or in the holy name of liberty or democracy?',
  'When someone you love dies, and you are not expecting it, you do not lose her all at once you lose her in pieces over a long time the way the mail stops coming, and her scent fades from the pillows and even from the clothes in her closet and drawers. '
]
for quote in quotes:
  response = lservice.documents().analyzeSentiment(
    body={
      'document': {
         'type': 'PLAIN_TEXT',
         'content': quote
      }
    }).execute()
  polarity = response['documentSentiment']['polarity']
  magnitude = response['documentSentiment']['magnitude']
  print('POLARITY=%s MAGNITUDE=%s for %s' % (polarity, magnitude, quote))