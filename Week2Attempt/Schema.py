# Schema.py implements the database

import sys, sqlite3, datetime
from sqlite3 import Error

# Set up tables and return connection
def createSchema():
	try:
		db = sqlite3.connect(':memory:')
	except Error as e:
		print(e)
		sys.exit(1)

	c = db.cursor()

	# pid is uid of parent account (authenticating Org or Admin)
	# Perms: bit string of length 4 such that 0=F/1=T in order <wxyz>
		# w: Admin Access (full access)
		# x: Orgizational Access (create/delete accounts)
		# y: Provider Access (create donations, et al.)
		# z: Receiver Access (claim donations, et al.)
	c.execute('''CREATE TABLE users(
		pid TEXT NOT NULL,
		perms INTEGER,
		uid TEXT NOT NULL UNIQUE, 
		hash TEXT)''')

	# barcodes contains title and unit type for barcoded items
	c.execute('''CREATE TABLE barcodes(
		code TEXT NOT NULL UNIQUE,
		title TEXT NOT NULL,
		units INTEGER NOT NULL)''')


	# did is associated donation id
	c.execute('''CREATE TABLE items(
		id INTEGER PRIMARY KEY,
		did INTEGER NOT NULL,
		barcode TEXT, 
		title TEXT NOT NULL, 
		count INTEGER NOT NULL, 
		units TEXT NOT NULL)''')

	c.execute('''CREATE TABLE donations(
		id INTEGER PRIMARY KEY, 
		provider TEXT NOT NULL, 
		receiver TEXT DEFAULT "pending",
		created TIMESTAMP,
		completed TIMESTAMP DEFAULT 0)''') 

	db.commit()
	c.close()
	return db
