import paramiko
from stat import S_ISDIR, S_ISREG
import re
from base64 import decodebytes
import json
import mariadb
db = mariadb.connect(
    host="localhost", user="wildserver", password="DBPassword", database="Unizeug"
)
c=db.cursor()
c.execute("DROP TABLE LVAs")
c.execute("CREATE TABLE LVAs(id BIGINT(20) unsigned NOT NULL AUTO_INCREMENT,lvid MEDIUMINT unsigned, lvname VARCHAR(256), lvpath VARCHAR(256),PRIMARY KEY(id))")
db.commit()
def get_dirstruct():
    with open("app/pwfile.json", "r") as f:
        cred = json.load(f)
    ssh = paramiko.SSHClient()
    print(cred["sftpurl"])
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # key=paramiko.RSAKey(data=decodebytes(bytes(cred["key"],"utf-8")))
    # ssh.get_host_keys().add(cred["sftpurl"], 'ssh-rsa', key)
    ssh.connect(cred["sftpurl"], username=cred["sftpuser"], password=cred["sftpPW"])
    sftp = ssh.open_sftp()
    folders = sftp.listdir_attr("/mnt/save/daten/Unizeug/")
    for entry in folders:
        if entry is None:
            continue
        if S_ISDIR(entry.st_mode):
            fname = str(entry.filename)
            regex=re.compile(r"Multimedia_only")
            if regex.search(fname):
                continue
            # print(fname)
            lvid = re.search(r"\d{3}.\d{3}", fname)
            # print(lvid)
            if lvid is None:
                continue
            lvid=int(lvid.group()[:3]+lvid.group()[4:])
            name=fname[:-8]
            print(name)
            print(lvid)
            cur=db.cursor()
            cur.execute("INSERT INTO LVAs (lvid, lvname, lvpath) VALUES(?,?,?)",(lvid,name,fname))
            db.commit()


if __name__ == "__main__":
    get_dirstruct()
