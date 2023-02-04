"""Entry Point for the module_0 flask app"""
import logging
import os
import shutil
from os.path import isfile, join

from flask import Flask, abort, jsonify, render_template, request, send_from_directory, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from config import DevConfig
from tiers.metier import get_true_arxive_id, get_article_from_semanticscholar, \
    tranform_dict_to_html
from tiers.pdf import get_metadata, get_watermark, get_text
from tiers.randomtext import get_random_string

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

MyConfig = DevConfig

app.config.from_object(MyConfig)


@app.errorhandler(409)  #
def error_409(error):
    """Customisation du message: no data yet to handle"""
    return "<h1>No data yet to handle</h1>", error


@app.errorhandler(410)  #
def error_410(error):
    """Customisation du message: no file part"""
    return "<h1>No file part</h1>", error


@app.errorhandler(411)
def error_411(error):
    """Customisation du message: no selected file"""
    return "<h1>No selected file</h1>", error


@app.errorhandler(412)
def error_412(error):
    """Customisation du message: file format not allowed"""
    return "<h1>file format not allowed</h1>", error


@app.errorhandler(413)
def error_413(error):
    """Customisation du message: file already uploaded"""
    return "<h1>file already uploaded</h1>", error


@app.errorhandler(414)
def error_414(error):
    """Customisation du message: file not uploaded"""
    return "<h1>file not uploaded</h1>", error


@app.errorhandler(415)  # todo c'est le 416 de HTTP. Il serait bon de s'aligner sur la norme...
def error_415(error):
    """Customisation du message: wrong range"""
    return "<h1>you don't have that many files on the server (wrong range)<h1>", error


@app.errorhandler(416)
def error_416(error):
    """Customisation du message: wrong range"""
    return "<h1>file too big<h1>", error


def allowed_file(filename):
    """Filter according to Config.ALLOWED_EXTENSIONS """
    # logger.info('allowed_file for {}'.format(filename))
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in MyConfig.ALLOWED_EXTENSIONS


def prettydoc(fonction):
    """Clean __doc__ to be used in a html file """
    txt = fonction.__doc__
    txt2 = []
    for line in txt.split("\n"):
        txt2.append(line.strip(" "))

    return "\n".join(txt2)


@app.route('/getarxiveid/<name>')
def get_arxive_id_for_file(name):
    """For 'recent' arXive file, extract watermark as JSON.
    It gives id (and version), categories, and date.
    :param:
    file name (in user session)
    :returns:
    json dictionary {"id": , "cat": , "date": }
    :Error:
    - 411 if there is no directory in session
    """
    if "directory" not in session:
        abort(411)
    name = name.replace(' ', '_')
    user_dir = session["directory"]
    watermark = get_watermark(user_dir + '/' + name)

    tab = watermark.split("  ")

    if len(watermark) == 0:
        mydic = {"id": "", "cat": "", "date": ""}
    else:
        mydic = {"id": tab[0], "cat": tab[1], "date": tab[2]}

    return jsonify(mydic)


@app.route('/getsemanticscholardata/<name>')
def get_semanticscholarfor_file(name):
    """For 'recent' arXive file, with watermark return paper's data as a dictionary
    WARNING Dictionary can be very big ! (eg with citation)
    :param:
    file name (in user session)
    :returns:
    paper's dictionary
    :Error:
    - 411 if there is no directory in session"""

    if "directory" not in session:
        abort(411)
    name = name.replace(' ', '_')
    user_dir = session["directory"]
    watermark = get_watermark(user_dir + '/' + name)

    true_info, _version = get_true_arxive_id(watermark)

    if len(true_info) == 0:
        return jsonify({})

    return jsonify(get_article_from_semanticscholar(true_info))


@app.route('/getserverfilenames')
def get_file_names():
    """As list of files may differ between server and client\
    gives list of server files for current session"""

    if "data" in session:
        return jsonify({session["data"]})

    return jsonify({})


@app.route('/getmetadata/<name>')
def get_metadata_for_file(name):
    """Return metadata of the file as JSON
    :returns:
    metadata as a json dictionary
    :Error:
    - 411 if there is no directory in session"""

    if "directory" not in session:
        abort(411)
    user_dir = session["directory"]
    metadata = get_metadata(user_dir + '/' + name)

    return jsonify(dict(metadata))


@app.route('/gettext/<name>')
def get_text_for_file(name):
    """Return Text of the file as JSON
    :returns:
    metadata as a json dictionary
    :Error:
    - 411 if there is no directory in session"""

    if "directory" not in session:
        abort(411)
    user_dir = session["directory"]
    text = get_text(user_dir + '/' + name)

    rvalue = {"/Text": text}
    return jsonify(rvalue)


@app.route('/startwfiles/<files>', methods=['POST', 'GET'])
def start2_files(files):
    """Ends the file selection phase. The list of files is given as an argument.
    :Example:
    POST /startwfiles/0709.4655.pdf&1009.4586.pdf
    :Error:
    - 411 if there is no directory in session"""
    logger.info("start2_files %s", files)

    tab_list_of_files = files.split("&")
    logger.debug("tabf=%s", tab_list_of_files)

    if "directory" not in session:
        abort(411)

    user_dir = session["directory"]

    if "data" in session:
        # logger.debug("start2_files redirect to url_for('start_job')")
        return jsonify({})  # redirect(url_for('start_job'))

    onlyfiles = [f for f in os.listdir(user_dir) if isfile(join(user_dir, f))
                 and allowed_file(f) and f in tab_list_of_files]
    # onlyfiles = []
    # logger.debug(user_dir)
    # for file in os.listdir(user_dir):
    # logger.debug("boucle file:{}".format(f))
    #    if not allowed_file(file):
    #        logger.debug("not allowed")
    #        continue
    #    if file not in tab_list_of_files:
    #        logger.debug("not in list")
    #        continue
    #    onlyfiles.append(file)

    # logger.debug("start2_files for {}".format(onlyfiles))

    corrected_data = "&".join(onlyfiles)
    if len(corrected_data) > 0:
        session["data"] = "&".join(onlyfiles)
        logger.debug("save data into session")
    else:
        logger.debug("no data to save into session")

    return jsonify({})


@app.route('/')
def home():
    """Start page for the app
    - if session has no data return uploadFile.html \
    (source https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask)
    - else return general start page for selected files (traitement.html)
    :Error:
    - 411 there is no directory in session"""
    logger.info("home(), methode %s", request.method)
    if "directory" in session:
        logger.info("known user")

        if "data" in session:
            return handle_file('1')

    logger.info("unknown user, create session[directory]  ")
    user_directory = MyConfig.UPLOAD_FOLDER + get_random_string(6)
    session["directory"] = user_directory

    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    return render_template('uploadFile.html')


@app.route('/doc', methods=['POST', 'GET'])
def get_doc():
    """Dynamically list server routes.
    :returns:
    render_template('doc.html',...)"""

    logger.info("getDoc")
    result = []

    sorted_rules = sorted(app.url_map.iter_rules(), key=lambda x: x.rule)

    for rule in sorted_rules:
        methods = ', '.join(rule.methods)
        current = {'route': rule.rule, 'endpoint': rule.endpoint, 'methods': methods,
                   'description': 'No description yet'}
        func = globals().get(str(rule.endpoint), None)
        if func is not None:
            current['description'] = prettydoc(func)

        result.append(current)

    return render_template('doc.html', routes=result)


@app.route('/upload', methods=['POST'])
def upload():
    """ upload a file
    :Error:
    - 410  no file part or file name
    - 411
    - 412 file type not in ALLOWED_EXTENSIONS
    - 413 file already exists"""
    logger.info("into upload_files")

    if "data" in session:
        logger.info("into upload_files data in session")

    try:
        if 'file' not in request.files:
            logger.info("into upload_files no file part")
            abort(410)
        # return redirect(request.url)
    except RequestEntityTooLarge:
        abort(416)
    else:
        logger.warning("unk erro in request.files")
    uploaded_file = request.files['file']

    # logger.info("uploaded_file={}".format(uploaded_file))

    #    for uploaded_file in request.files.getlist('file'):
    #        if uploaded_file.filename != '':
    #            uploaded_file.save(uploaded_file.filename)

    filename = secure_filename(uploaded_file.filename)
    if filename == '':
        abort(411)

    if not allowed_file(filename):
        abort(412)

    if "directory" not in session:

        user_directory = MyConfig.UPLOAD_FOLDER + get_random_string(6)
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)
        logger.info("upload_files recreate folder")
        session["directory"] = user_directory
    else:
        user_directory = session["directory"]

    fullname = os.path.join(user_directory, filename)

    if os.path.exists(fullname):
        logger.info("upload_files abort(413), fullName=%s", fullname)
        abort(413)

    logger.info("upload_files %s", fullname)

    uploaded_file.save(fullname)
    return jsonify({})


@app.route('/remove/<file>', methods=['POST', 'GET'])
def remove(file):
    """Remove a file from server.
    :Error:
    - 411 there is no directory in session
    - 413 no directory in session
    """
    logger.info("remove %s, %s", file, request.method)

    if "directory" not in session:
        logger.warning("error on remove no directory")
        abort(411)

    user_directory = session["directory"]

    fullname = os.path.join(user_directory, file)
    fullname = fullname.replace(' ', '_')
    if not os.path.exists(fullname):
        logger.warning("error on remove %s", fullname)
        abort(414)

    logger.info("delete file %s", fullname)

    os.remove(fullname)  # todo handle error

    return jsonify({})


#
# @app.route('/startJob', methods=['POST', 'GET'])  # todo pra a priori ne sert plus
# def start_job():
#     """Do nothing yet...
#     :Error:
#     - 411 there is no directory in session"""
#     logger.info("startJob, %s", request.method)
#
#     if "directory" not in session:
#         logger.warning("startJob no directory abort (411)")
#         abort(411)
#
#     user_dir = session["directory"]
#
#     onlyfiles = [f for f in os.listdir(user_dir) if isfile(join(user_dir, f)) and allowed_file(f)]
#
#     logger.info("startJob for %s", onlyfiles)
#
#     # return render_template('uploadedFile.html', data=onlyfiles), 200
#     return render_template('traitement.html', data=onlyfiles), 200
#
#     # return jsonify({}), 202, {'Location': url_for('refreshClient', task_id=taskId)}


@app.route('/download/<name>')
def download_file(name):
    """Download File name\nFor futur use (we do not modify files yet).
    :returns:
    file if in user session."""
    logger.info("download_file for {%s}", name)
    user_dir = session["directory"]
    return send_from_directory(MyConfig.UPLOAD_FOLDER + user_dir, name, as_attachment=True)


@app.route('/handle/<num>')
def handle_file(num):
    """Main processing. (Nothing now)
    :param : id of the file to handle (start at 1)"""
    logger.info('handleFile for {%s}', num)
    if "directory" in session:
        logger.info("known user")

        if "data" in session:
            files = session["data"]
            if len(files) == 0:
                abort(411)
            tab_list_of_files = files.split("&")
            logger.info("home has data %s", tab_list_of_files)
            user_directory = session["directory"]
            _sem_schol_extract = ""
            # sem_schol_ref = ""
            sem_dic = ""

            if int(num) > len(tab_list_of_files):
                abort(415)

            file = tab_list_of_files[int(num) - 1]

            # for file in tab_list_of_files:
            fullname = os.path.join(user_directory, file)
            fullname = fullname.replace(' ', '_')

            res = get_watermark(fullname)
            logger.info("watermark %s", res)

            metadata = get_metadata(fullname)
            text = get_text(fullname)

            true_info, _version = get_true_arxive_id(res)

            # if len(true_info) != 0:
            #    _sem_schol_extract, sem_schol_ref = get_content_from_semanticscholar(true_info)
            #    # logger.info("Semanticscholar : {}".format(dataSemanticscholar))
            #    logger.info("true info %s", true_info)
            if len(true_info) != 0:
                sem_dic = get_article_from_semanticscholar(true_info)
                # tempo debug
                # v = sem_dic.get("references")
                # v2 = {"references":v[:1]}
                sem_dic = tranform_dict_to_html(sem_dic, "<h2>", "</h2>", ['citations'])

            # session.pop("data") # faire un pop data file ?
            # return render_template('uploadedFile.html', data=tabListOfFiles,)

            # print("**metadata**")
            # print(metadata)

            return render_template('traitement.html',
                                   data=tab_list_of_files,
                                   dataMeta=metadata,
                                   dataTexte=text,
                                   datatab3=sem_dic)

    return '<h1>La session a été effacée. Vous devez recharger de nouveaux fichiers ...</h1>'


@app.route('/delete_session')
def delete_session():
    """Destroy the user's session. For debug purpose.
    :returns:
    '<h1>Session deleted!</h1>'"""

    session.pop('data', default=None)
    if "directory" in session:
        directory = session["directory"]
        if os.path.exists(directory):
            shutil.rmtree(directory)
    session.pop("directory", default=None)
    return '<h1>Session deleted!</h1>'


def my_init():
    """In production deletes all files each time the server is launched.
    (TODO we should erase more often!)
    """
    if os.path.exists(MyConfig.UPLOAD_FOLDER):
        shutil.rmtree(MyConfig.UPLOAD_FOLDER)
    if not os.path.exists(MyConfig.UPLOAD_FOLDER):
        os.makedirs(MyConfig.UPLOAD_FOLDER)


if __name__ == '__main__':
    my_init()
    app.run(debug=False,host='0.0.0.0', port=5000)
