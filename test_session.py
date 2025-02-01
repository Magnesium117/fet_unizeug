# coding: utf-8
import mariadb
db=mariadb.connect(host="localhost",user="wildserver",password:"DBPassword",database="Unizeug")
db=mariadb.connect(host="localhost",user="wildserver",password="DBPassword",database="Unizeug")
cur=db.cursor()
cur.execute("Select id form FIP where filename='VO_Mathematik_3.pdf';")
cur.execute("Select id form FIP where filename=?;",("VO_Mathematik_3.pdf"))
cur.execute("Select id form FIP where filename=?;",("VO_Mathematik_3.pdf",))
cur.execute("Select id form FIP Where filename=?;",("VO_Mathematik_3.pdf",))
cur.execute("Select id form FIP Where filename=?;",("VO_Mathematik_3.pdf"))
cur.execute("Select id form FIP Where filename=?;",("VO_Mathematik_3.pdf",))
cur.execute("Select id from FIP Where filename=?;",("VO_Mathematik_3.pdf",))
cur.fetchone()
cur.fetchone()
cur.execute("show tables;")
cur.fetchone()
cur.fetchone()
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.fetchone()#
cur.execute("insert into FIP filename Values(?);",("test",))
cur.execute("insert into FIP (filename) Values(?);",("test",))
cur.fetchone()
cur.execute("Select * from FIP Where filename=?;",("VO_Mathematik_3.pdf",))
cur.fetchone()
cur.execute("Select * from FIP Where id=?;",("b78c869f-e0bb-11ef-9b58-84144d05d665",))
cur.fetchone()
get_ipython().run_line_magic('save', '')
