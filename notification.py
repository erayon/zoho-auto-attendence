import subprocess, json, platform
from flask import Flask, request
#from win10toast import ToastNotifier
from gevent.pywsgi import WSGIServer
app = Flask(__name__)

@app.route('/notify',methods=['POST'])
def notify():
    content = request.json
    urgency = content['urgency']
    title = content['title']
    message = content['message']
    if platform.system() == 'Linux':
        subprocess.Popen(['notify-send','--urgency={}'.format(urgency) ,title,message])
        return json.dumps({'res':True})
    # if platform.system() == 'Windows':
    #     toast = ToastNotifier()
    #     toast.show_toast(title,message)
    #     return json.dumps({'res':True})

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 12345), app)
    http_server.serve_forever() 