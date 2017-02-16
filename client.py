import http.client
import urllib.parse
import json
import pprint
import os
from base import base


def send_message(endpoint, message):
    conn = http.client.HTTPConnection("localhost", 18080)
    conn.request("PUT", endpoint, json.dumps(message).encode('utf-8'))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if response.status != 200:
        print(response, data)
        return False
    else:
        return True


def get_message():
    conn = http.client.HTTPConnection("localhost", 18080)
    conn.request("GET", "/events")
    response = conn.getresponse()
    data = response.read()
    conn.close()

    if response.status != 200:
        print(response, data)
        return None
    else:
        return json.loads(data.decode('utf-8'))


def get_sound_path(filename):
    # get path to sound files that are in the same directory as the python
    # script
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)


send_message('/configure', {
    "credentials": {
        "app_id": "id",
        "app_key": "key"
    },
    "wakeup": {
        "phrases": [
            'hey dragon',
            'hello dragon',
            'hey jarvis',
            'hello jarvis',
            'jarvis'
        ],
        "beep": get_sound_path('listen.pcm'),
    },
    "recognition": {
        "context_tag": "M3252_A1653_V1"
    },
})

send_message('/output/file', {'path': get_sound_path('startup.pcm')})
# send_message('/recognize', {}) #'beep': get_sound_path('startup.pcm')})

listening = False
while True:
    message = get_message()
    if message is None:
        break
    pprint.pprint(message)

    if message['event'] == 'recognition_state':
        if message['state'] == 'listening_for_speech':
            spoken_text = None
            intent = None
            listening = True
        elif message['state'] == 'processing_speech':
            send_message('/output/file',
                         {'path': get_sound_path('processing.pcm')})
            listening = False

        elif message['state'] == 'waiting_for_wakeup':
            if listening:
                send_message('/output/file',
                             {'path': get_sound_path('timeout.pcm')})
            listening = False

    elif message['event'] == 'recognition_result':
        spoken_text = message.get('transcriptions', [None])[0]
        if spoken_text is not None:
            send_message('/output/synthesize',
                         {'text': 'You said %s' % (spoken_text,)})
        else:
            send_message('/output/file',
                         {'path': get_sound_path('no_utt.pcm')})

    elif message['event'] == 'understanding_result':
        intent = message.get('nlu_interpretation_results', {}).get('payload', {}).get(
            'interpretations', [{}])[0].get('action', {}).get('intent', {}).get('value')
        response_json = message.get('nlu_interpretation_results', {}).get(
            'payload', {}).get('interpretations', [{}])[0]
        client = base(response_json)
        client.parse_request()
        if intent is not None:
            send_message('/output/synthesize',
                         {'text': 'I am on my way'})
            if intent == 'NO_MATCH':
                send_message('/output/file',
                             {'path': get_sound_path('no_nlu.pcm')})
            else:
                send_message('/output/file',
                             {'path': get_sound_path('success.pcm')})
        else:
            send_message('/output/file',
                         {'path': get_sound_path('no_nlu.pcm')})


