import os
from config import DevConfig, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from tiers.pdf import getWatermark, getMetadata

app = Flask(__name__)
app.config.from_object(DevConfig)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/UPLOAD_FOLDER/<name>')
def download_file(name):
    watermark = getWatermark(UPLOAD_FOLDER+name)

    tab = watermark.split("  ")
    print('watermark=',tab,len(tab))
    arXiveData = False
    if len(tab) == 3:
        print(tab[0],tab[1],tab[2])
        if tab[0].startswith("arXiv:"):
            arXiveData = True

    returnText = ""

    if arXiveData: # title c'est le nom de l'onglet !
       returnText = '''
    <!doctype html>
    <title>Vous avez upload un fichier </title>       # c'est le nom de l'onglet !
    <h1>L'id arxive est {}</h1>
    <h1>de (les) rubrique(s) {}</h1>
    <h1>en date du {}</h1>  
    '''.format(tab[0],tab[1],tab[2])
    else:
        returnText=  '''<!doctype html>
    <title>Vous n'avez pas upload un fichier arXive (récent) </title>      
    <h1>Vous avez uploader un fichier</h1>
    '''

    metadata = getMetadata(UPLOAD_FOLDER+name)

    metadataText = """Les metadonnées du fichier sont"""
    if len(metadata) > 0:
        for k,v in metadata.items():
            metadataText = metadataText + '\n' + """<h1>{} : {} </h1>""".format(k,v)


    return returnText +  metadataText


 #   return send_from_directory(UPLOAD_FOLDER, name)  # lance dans l'explorateur le fichier téléchargé.

#TODO PRA ?
#If you’re using middleware or the HTTP server to serve files, you can register the download_file endpoint as build_only so url_for will work without a view function.
#app.add_url_rule("/UPLOAD_FOLDER/<name>", endpoint="download_file", build_only=True)




@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        print("request.url:",request.url)
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
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
                # TODO si le fichier est déjà la ????
            filename = secure_filename(file.filename) # secure_filename('../../../../home/username/.bashrc') en 'home_username_.bashrc' !
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/old')
def home():
    username = request.cookies.get('username')
    for k, v in request.cookies.items():
        print(k,v)
    print("Username :", username)
    return '<h1>Hello World!</h1>'



if __name__ == '__main__':
    app.run()