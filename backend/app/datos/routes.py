import os
import secrets

from flask import current_app, g, jsonify, request
from werkzeug.utils import secure_filename

from . import datos
from ..auth.decorators import jwt_valid_token_access

ZIP_MAGIC = (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08')
OLE_MAGIC = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'


def allowed_file(filename):
  filename = secure_filename(filename)
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def secure_name(filename):
  original = secure_filename(filename)
  _, file_extension = os.path.splitext(original)
  return '{}{}'.format(secrets.token_hex(16), file_extension.lower())


def _content_matches_extension(filename, stream):
  """Valida el contenido real, no solo la extensión declarada."""
  extension = os.path.splitext(secure_filename(filename))[1].lower()
  head = stream.read(2048)
  stream.seek(0)

  if extension == '.xlsx':
    return head.startswith(ZIP_MAGIC)
  if extension == '.xls':
    return head.startswith(OLE_MAGIC)
  if extension in ('.csv', '.txt'):
    # Los formatos de texto no deben contener bytes nulos (binario disfrazado).
    return len(head) > 0 and b'\x00' not in head
  return False


def _stream_size(stream):
  position = stream.tell()
  stream.seek(0, os.SEEK_END)
  size = stream.tell()
  stream.seek(position)
  return size


@datos.route('/subir', methods=['POST'])
@jwt_valid_token_access
def subir():
  upload_folder = current_app.config['UPLOAD_FOLDER']
  os.makedirs(upload_folder, exist_ok=True)

  max_file_size = int(current_app.config['MAX_FILE_SIZE'])
  files_upload = []

  for key in request.files:
    myfile = request.files[key]
    if not myfile.filename or not allowed_file(myfile.filename):
      files_upload.append({"file": myfile.filename, "disk": "error"})
      continue

    try:
      if _stream_size(myfile.stream) > max_file_size:
        files_upload.append({"file": myfile.filename, "disk": "error"})
        continue
      if not _content_matches_extension(myfile.filename, myfile.stream):
        files_upload.append({"file": myfile.filename, "disk": "error"})
        continue
    except (OSError, ValueError):
      files_upload.append({"file": myfile.filename, "disk": "error"})
      continue

    filename = secure_name(myfile.filename)
    myfile.save(os.path.join(upload_folder, filename))
    files_upload.append({"file": myfile.filename, "disk": filename})

  current_app.logger.info(
    'upload user_id=%s ip=%s files=%s',
    g.current_user.id,
    request.remote_addr,
    len(files_upload)
  )
  return jsonify({"msg": "_UPLOAD_FILE", "file": files_upload}), 200
