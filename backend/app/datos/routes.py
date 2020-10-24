import os
import hashlib
import random
from datetime import datetime, timedelta
from . import datos
from flask import jsonify, request, redirect
from app import Config
from ..auth.decorators import jwt_valid_token_access

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def secure_name(filename):
    timestamp = datetime.timestamp(datetime.now())
    basefilename, file_extension= os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(10))
    randomstr = hashlib.md5(randomstr.encode() + str(timestamp).encode()).hexdigest()
    return '{randomstring}{ext}'.format(basename=basefilename, randomstring=randomstr, ext=file_extension)


@datos.route('/subir', methods=['POST'])
@jwt_valid_token_access
def subir():
    files = request.files
    filesUpload = []
    for f in files:
      myfile = files[str(f)]
      if myfile.filename != '':
        if myfile and allowed_file(myfile.filename):
          filename = secure_name(myfile.filename)
          myfile.save(os.path.join(Config.UPLOAD_FOLDER, filename))
          filesUpload.append({"file": myfile.filename, "disk": filename})
        else:
          filesUpload.append({"file": myfile.filename, "disk": "error"})
      else:
        filesUpload.append({"file": myfile.filename, "disk": "error"})

    return jsonify({"msg": "_UPLOAD_FILE", "file": filesUpload}), 200