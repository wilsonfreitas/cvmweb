
import io
import zipfile
import urllib.request
import tempfile


def download_unzip(url):
    temp = tempfile.TemporaryFile()
    with urllib.request.urlopen(url) as res:
        temp.write(res.read())
        temp.seek(0)
    zf = zipfile.ZipFile(temp)
    name = zf.namelist()[0]
    content = zf.read(name)
    zf.close()
    temp.close()
    return content
