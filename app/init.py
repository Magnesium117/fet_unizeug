import paramiko
from stat import S_ISDIR, S_ISREG
import re

# from base64 import decodebytes
import json
import mariadb

CATEGORIES = [
    "Prüfungen",
    "Klausuren",
    "Übungen",
    "Labore",
    "Unterlagen",
    "Zusammenfassungen",
    "Multimedia",
]
SUBCAT_CATEGORIES = ["Klausuren", "Übungen", "Labore"]
unizeug_path = "/mnt/save/daten/Unizeug/"
db = mariadb.connect(
    host="localhost", user="wildserver", password="DBPassword", database="Unizeug"
)
c = db.cursor()
try:
    c.execute("DROP TABLE LVAs")
except mariadb.OperationalError:
    pass
c.execute(
    "CREATE TABLE LVAs(id BIGINT(20) unsigned NOT NULL AUTO_INCREMENT,lvid VARCHAR(6), lvname VARCHAR(256), lvpath VARCHAR(256),PRIMARY KEY(id))"
)
try:
    c.execute("DROP TABLE Profs")
except mariadb.OperationalError:
    pass
c.execute(
    "CREATE TABLE Profs(id BIGINT(20) unsigned NOT NULL AUTO_INCREMENT,name VARCHAR(256),PRIMARY KEY(id))"
)
try:
    c.execute("DROP TABLE LPLink")
except mariadb.OperationalError:
    pass
c.execute(
    "CREATE TABLE LPLink(id BIGINT(20) unsigned NOT NULL AUTO_INCREMENT,LId bigint(20),PId bigint(20),PRIMARY KEY(id))"
)
try:
    c.execute("DROP TABLE SubCats")
except mariadb.OperationalError:
    pass
c.execute(
    "CREATE TABLE SubCats(id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,LId BIGINT(20),PId BIGINT(20),cat TINYINT UNSIGNED,name VARCHAR(256), PRIMARY KEY(id))"
)
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
    folders = sftp.listdir_attr(unizeug_path)
    for entry in folders:
        if entry is None:
            continue
        if not S_ISDIR(entry.st_mode):
            continue
        fname = str(entry.filename)
        regex = re.compile(r"Multimedia_only")
        if regex.search(fname):
            continue
        # print(fname)
        lvid = re.search(r"[a-zA-Z0-9]{3}\.[a-zA-Z0-9]{3}", fname)
        print(lvid)
        if lvid is None:
            continue
        lvid = lvid.group()[:3] + lvid.group()[4:]
        name = fname[:-8]
        # print(name)
        # print(lvid)
        cur = db.cursor()
        cur.execute(
            "INSERT INTO LVAs (lvid, lvname, lvpath) VALUES(?,?,?)", (lvid, name, fname)
        )
        cur.execute("SELECT id FROM LVAs WHERE lvid=?", (lvid,))
        lid = cur.fetchone()[0]
        db.commit()
        for profsdir in sftp.listdir_attr(unizeug_path + fname + "/"):
            if profsdir is None or not S_ISDIR(profsdir.st_mode):
                continue
            # print(profsdir.filename)
            try:
                lastname, firstname = re.split(r"[_\-\s]", str(profsdir.filename))
                pid = link_prof(firstname, lastname, lid)
            except ValueError:
                print(f"{name} is broken")
                continue
            for cat in sftp.listdir_attr(
                unizeug_path + fname + "/" + profsdir.filename + "/"
            ):
                if cat is None or not S_ISDIR(cat.st_mode):
                    continue
                if cat.filename not in SUBCAT_CATEGORIES:
                    continue
                idx = CATEGORIES.index(cat.filename)
                for subcat in sftp.listdir_attr(
                    unizeug_path
                    + fname
                    + "/"
                    + profsdir.filename
                    + "/"
                    + cat.filename
                    + "/"
                ):
                    if subcat is None or not S_ISDIR(subcat.st_mode):
                        continue
                    cur = db.cursor()
                    cur.execute(
                        "INSERT INTO SubCats (LId,PId,cat,name) VALUES(?,?,?,?)",
                        (lid, pid, idx, subcat.filename),
                    )
                db.commit()


def link_prof(firstname, lastname, lid):
    cur = db.cursor()
    cur.execute("SELECT id from Profs WHERE name=?", (lastname + " " + firstname,))
    res = cur.fetchone()
    if res is not None:
        cur.execute("INSERT INTO LPLink (LId,PId) VALUES(?,?)", (lid, res[0]))
        db.commit()
        return res[0]
    cur.execute("SELECT id from Profs WHERE name=?", (firstname + " " + lastname,))
    res = cur.fetchone()
    if res is not None:
        cur.execute("INSERT INTO LPLink (LId,PId) VALUES(?,?)", (lid, res[0]))
        db.commit()
        return res[0]
    cur.execute("INSERT INTO Profs (name) VALUES(?)", (lastname + " " + firstname,))
    cur.execute("SELECT id FROM Profs WHERE name=?", (lastname + " " + firstname,))
    res = cur.fetchone()
    cur.execute("INSERT INTO LPLink (LId,PId) VALUES(?,?)", (lid, res[0]))
    db.commit()
    return res[0]


if __name__ == "__main__":
    get_dirstruct()
