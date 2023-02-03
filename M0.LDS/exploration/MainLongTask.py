import logging
import random
import time
from threading import Thread

from flask import Flask, request, url_for, jsonify, render_template

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
app = Flask(__name__)

bufferedData = {}
taskId = -1

"""sur la base de https://blog.miguelgrinberg.com/post/using-celery-with-flask
mais sans celery !
"""


def long_task(myid, elementid, userid):
    global bufferedData

    logger.info("in long_task {} {} {}".format(taskId, elementid, userid))

    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = '{0} {1} {2}...'.format(random.choice(verb),
                                      random.choice(adjective),
                                      random.choice(noun))
    total = random.randint(10, 30)
    for i in range(total):
        meta = {'current': i, 'total': total, 'status': message,
                'elementid': elementid, 'userid': userid, 'state': 'PROGRESS'}
        bufferedData[myid] = meta
        logger.debug("in long_task {}/{}".format(i, total))
        logger.debug("apres l'action")
        time.sleep(1)

    meta = {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42, 'elementid': elementid, 'userid': userid}
    logger.info("in long_task last")
    bufferedData[myid] = meta
    logger.info("apres l'action")
    return


@app.route('/refresh/<task_id>')
def refreshClient(task_id):
    global bufferedData
    logger.debug("refreshClient id {} size {}".format(task_id, len(bufferedData)))
    data = bufferedData.get(str(task_id), None)

    bufferedData[str(task_id)] = None
    if data is not None:
        return data

    return jsonify({}), 202, {'Location': url_for('refreshClient', task_id=taskId)}


@app.route('/longtask', methods=['POST'])  # avant seulement post
def longtask():
    logger.info("entering longtask '/longtask'")
    global taskId  # , threads
    taskId = taskId + 1
    logger.debug("data {}, form {} taskId {} ".format(request.get_data(as_text=True), request.form, taskId))

    elementid = 0  # request.json['elementid']
    userid = 0  # request.json['userid']

    logger.debug("avant creation du thread {}".format(taskId))

    t = Thread(target=long_task,
               args=(str(taskId), elementid, userid))
    logger.debug("apres creation du thread {}".format(taskId))

    t.start()
    logger.debug("apres le start du thread {}".format(taskId))

    # Le locate va faire que le client web va vaire un get sur l'URL
    return jsonify({}), 202, {'Location': url_for('refreshClient', task_id=taskId)}


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
