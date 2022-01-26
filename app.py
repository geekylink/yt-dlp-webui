from flask import Flask, render_template, request, send_file
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

def RunCMD(cmd: str, timeout = 15):
    """
        Runs a command, captures stdout & stderr, trims output
        timeout: how long to let command run, -1 for infinite
    """

    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

    try:
        if timeout == -1:
            outs, errs = proc.communicate()
        else:
            outs, errs = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    outs = outs.decode("UTF-8").strip()
    errs = (errs.decode("UTF-8").strip() if errs else None)

    return {"out": outs, "err": errs, "ret": proc.returncode}


app = Flask(__name__)


def save_file():
    link = request.args.get("link")
    audioOnly = request.args.get("audioOnly") != None

    cmd = "yt-dlp "

    if audioOnly:
        cmd += "-x "
    cmd += "\"" + link + "\""

    # Trigger download
    print("Executing: " + cmd)
    res = RunCMD(cmd, -1)

    output = res["out"].split("\n")
    fileName = ""
    for i in range(len(output)):
        if not audioOnly and output[i].startswith("Destination:"):
            print("downloaded video")
            fileName = output[i][12:].strip()
        if not audioOnly and output[i].startswith("[download]"):
            print("already downloaded")
            fileName = output[i][11:output[i].find(" has already been downloaded")].strip()
        if audioOnly and output[i].startswith("[ExtractAudio]"):
            print("downloaded audio")
            fileName = output[i][output[i].find("Destination:")+13:].strip()
            

    print("file: ", fileName)

        #fileName = fileNamePre[fileNamePre.find("Destination:")+12:].strip()

    if request.args.get("downloadOnly"):
        return "Downloaded " + link + " to: " + fileName

    return send_file(fileName)

@app.route('/')
def index_video():
    if not request.args.get("link"):
        return render_template("index.html")

    return save_file()

@app.route('/music')
def index_music():
    if not request.args.get("link"):
        return render_template("index.html", mode="audio")

    return save_file()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
