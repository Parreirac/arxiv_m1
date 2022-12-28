from threading import Thread

from flask import json, make_response
import os
import time
import random

from requests import post

# from threading import Thread
# from typing import List, Any

from config import DevConfig
from flask import Flask, flash, request, redirect, url_for, jsonify, render_template
from werkzeug.utils import secure_filename
# from flask import send_from_directory
from tiers.pdf import getWatermark, getMetadata
# import  tiers.ThreadWithReturnValue as MyThread
# from celery import Celery

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(DevConfig)

# logger = get_task_logger(__name__)

bufferedData = []
taskId = -1


# endedLongTask = {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}

def mySafePost(url, jsondata):
    try:
        post(url, json=jsondata)
    except Exception as inst:
        logger.error("error un mySafePost")
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)


def long_task(di, elementid, userid, lurl):
    # global endedLongTask
    logger.info("in long_task {} {} {} {}".format(di, elementid, userid, lurl))

    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 30)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        meta = {'current': i, 'total': total, 'status': message,
                'elementid': elementid, 'userid': userid, 'state':'PROGRESS'}
        logger.info("in long_task {}/{}".format(i, total))
        mySafePost(lurl, jsondata=meta)  # json=meta)data = meta,
        # make_response(jsonify(meta), 200)
        logger.info("apres l'action")
        time.sleep(1)

    meta = {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42, 'elementid': elementid, 'userid': userid}
    logger.info("in long_task last")
    mySafePost(lurl, jsondata=meta)
    # mySafePost(lurl,   jsondata = meta)#  json=meta)data = meta,
    # make_response(jsonify(meta), 200)
    logger.info("apres l'action")
    return meta


@app.route('/status', methods=['GET', 'POST'])
def taskstatus():
    global bufferedData
    print("taskstatus:")
    print("0:", request)
    print("1:", request.data)
    print("2:", len(bufferedData))
    # print("2:", request.get_data(as_text=True)) # retourne un dico
    # print("3:", request.get_json()) # retourne un dico
    # print("2;",request.json )

    # return make_response(jsonify(d), 200)

    # userid = request.json['userid']
    data = request.json
    # print("data:", data)
    # ns = app.clients.get(userid)
    bufferedData.append(make_response(jsonify(data), 200))
    return jsonify({}), 202


#    r = make_response(jsonify(data), 200)
#    return make_response(jsonify(data), 200)
# {'current': i, 'total': total, 'status': message,'elementid': elementid, 'userid': userid}
# return jsonify(data),  200 , {'Location': url_for('upload_file',_external=True)}


#   return 'ok'
#   return 'error', 404
@app.route('/___status/<task_id>')
def taskstatus__(task_id):
    # global threads
    # print('taskstatus pour :', task_id, type(taskId), request.get_data(as_text=True))
    # print("threads.len =", len(threads))

    t = task_id
    for th in []:  # threads:
        print("th.name=", th.name)
        if th.name == str(taskId):
            t = th
            break

    if t is None:
        print("t is None")
        response = {
            'state': 'FAILURE ',
            'current': 1,
            'total': 1,
            'status': ' ',  # this is the exception raised  todo pra redondant avec state ? a renommer en error ?
            'result': 'computing'
        }
    else:
        print("t is not None")
        try:
            res = t.join()
            print('res=', res)
            response = {
                'state': 'Task completed ',
                'current': res['current'],
                'total': res['total'],
                'status': ' ',  # this is the exception raised
                'result': res['result']
            }
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,

    # TODO je n'utilise pas result !

    return  # jsonify(response)


@app.route('/refresh/<task_id>')
def refreshClient(task_id):
    global bufferedData
    logger.info("refreshClient id {} size {}".format(task_id, len(bufferedData)))
    data = bufferedData.pop()
    bufferedData.clear()
    return data


@app.route('/longtask', methods=['POST'])  # avant seulement post
def longtask():
    logger.info("entering longtask '/longtask'")
    global taskId # , threads
    taskId = taskId + 1
    logger.info("data {}, form {} taskId {} ".format(request.get_data(as_text=True), request.form, taskId))

    di = {'id': taskId, 'state': 'PENDING', 'meta': ''}

    elementid = 0  # request.json['elementid']
    userid = 0  # request.json['userid']
    truc = url_for('taskstatus', _external=True)
    # C'est le nom d'une fonction pas la route directement
    # en faisant un external j'ai un http://127.0.0.1:5000/status  plutot qu'un /Status
    logger.info("avant creation du thread {} truc {}".format(taskId, truc))
    # t = MyThread.ThreadWithReturnValue(target=long_task, args=(di,elementid, userid, truc ), name = str(taskId))
    t = Thread(target=long_task, args=(di, elementid, userid, truc), name=str(taskId))
    logger.info("apres creation du thread {}".format(taskId))
    #    threads.append( t)
    t.start()
    logger.info("apres le start du thread")

    return jsonify({}), 202, {'Location': url_for('refreshClient', task_id=taskId)}  # provoque un GET /status HTTP/1.1
    # return jsonify({}), 200


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in DevConfig.ALLOWED_EXTENSIONS


@app.route('/UPLOAD_FOLDER/<name>')
def download_file(name):
    watermark = getWatermark(DevConfig.UPLOAD_FOLDER + name)

    tab = watermark.split("  ")
    print('watermark=', tab, len(tab))
    arXiveData = False
    if len(tab) == 3:
        print(tab[0], tab[1], tab[2])
        if tab[0].startswith("arXiv:"):
            arXiveData = True

    if arXiveData:  # title c'est le nom de l'onglet !
        returnText = '''
    <!doctype html>
    <title>Vous avez upload un fichier </title>       # c'est le nom de l'onglet !
    <h1>L'id arxive est {}</h1>
    <h1>de (les) rubrique(s) {}</h1>
    <h1>en date du {}</h1>  
    '''.format(tab[0], tab[1], tab[2])
    else:
        returnText = '''<!doctype html>
    <title>Vous n'avez pas upload un fichier arXive (récent) </title>      
    <h1>Vous avez uploader un fichier</h1>
    '''

    metadata = getMetadata("." + DevConfig.UPLOAD_FOLDER + name)

    metadataText = """Les metadonnées du fichier sont"""
    if len(metadata) > 0:
        for k, v in metadata.items():
            metadataText = metadataText + '\n' + """<h1>{} : {} </h1>""".format(k, v)

    return returnText + metadataText


#   return send_from_directory(UPLOAD_FOLDER, name)  # lance dans l'explorateur le fichier téléchargé.

# TODO PRA ?
# If you’re using middleware or the HTTP server to serve files, you can register the download_file endpoint as build_only so url_for will work without a view function.
# app.add_url_rule("/UPLOAD_FOLDER/<name>", endpoint="download_file", build_only=True)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    logger.info("in upload_file (route /)")
    if request.method == 'GET':
        return render_template('index.html')  # TODO , email=session.get('email', ''))

    if request.method == '___POST':  # TODO PRA ici ???

        print("request.url:", request.url)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if not os.path.exists("." + DevConfig.UPLOAD_FOLDER):
                os.makedirs("." + DevConfig.UPLOAD_FOLDER)
                # TODO si le fichier est déjà la ????
            filename = secure_filename(
                file.filename)  # secure_filename('../../../../home/username/.bashrc') en 'home_username_.bashrc' !
            file.save(os.path.join("." + DevConfig.UPLOAD_FOLDER, filename))
            return redirect(url_for('download_file', name=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>'''

    return redirect(url_for('index'))


@app.route('/old')
def home():
    username = request.cookies.get('username')
    for k, v in request.cookies.items():
        print(k, v)
    print("Username :", username)
    return '<h1>Hello World!</h1>'


@app.route('/summary')
def summary():
    data = ""  # make_summary()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response  # ou return make_response(jsonify(d), 200) si d est un dico


if __name__ == '__main__':
    app.run(debug=True)
