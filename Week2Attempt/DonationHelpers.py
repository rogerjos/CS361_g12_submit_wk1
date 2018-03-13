# DonationHelpers.py implements helper functions for manipulating the donation/item/barcode tables

import datetime # For creation/completed donation timestamps

# Functions:
# addBarcode()
# addDonation()
# addItemByManual()
# addItemByBarcode()
# listProviderDonations
# getDonationItems()
# claimDonation()
# existDonation()
# existItem()
# existBarcode()

# Function addBarcode()
# Purpose: insert a new barcode entry into the barcodes table
# Syntax: addBarcode(<connection>, <barcode>, <title>, <units>)
# Returns: True if item inserted, else False
def addBarcode(db, code, title, units):

	# Check for existing barcode
	c = db.cursor()
	c.execute('''SELECT * FROM barcodes WHERE code = ?''', (code,))
	if c.fetchone() is not None:
		c.close()
		return False

	# Add barcode 
	c.execute('''INSERT into barcodes(code, title, units) VALUES(?,?,?)''', (code, title, units))
	
	# Test success
	c.execute('''SELECT * FROM barcodes WHERE code = ?''', (code,))
	result = c.fetchone()
	db.commit
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function addDonation()
# Purpose: Creates a new donation in donation table
# Syntax: addDonation(<connection>, <provider>, <receiver>)
# Returns: donation.id if donation is successfully created, else -1
# Note: receiver should be None unless receiver is known in advance
def addDonation(db, provider, receiver):
	
	c = db.cursor()
	
	if receiver is None:	
		# If no receiver specified
		c.execute('''INSERT INTO donations(provider, created) VALUES(?,?)''', (provider, datetime.datetime.now()))
	else:	
		# If receiver specified
		c.execute('''INSERT INTO donations(provider, receiver, created) VALUES(?,?,?)''', (provider, receiver, datetime.datetime.now))
	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1

# Function addItemByManual()
# Purpose: add a new item to the items table without barcode
# Syntax: addItemByManual(<connection>, <donation_id>, <title>, <count>, <unit_type>)
# Returns: item.id if item is successfully created, else -1
# Note: Fails if invalid donation_id
def addItemByManual(db, did, title, count, unit):

	if not existDonation(db, did):
		return -1

	# Test for matching item in table
	c = db.cursor()
	c.execute('''SELECT id, count FROM items WHERE did=? AND title=? AND units=?''', (did, title, unit))
	result = c.fetchone()

	# Item in table: add count to existing item
	if result is not None: 
		newCount = result[1] + count
		c.execute('''UPDATE items SET count = ? WHERE id = ?''', (newCount, result[0]))

	# Item not in table: add new item to table
	else:
		c.execute('''INSERT INTO items(did, title, count, units) VALUES(?,?,?,?)''', (did, title, count, unit))

	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1

# Function addItemByBarcode()
# Purpose: add a new item to the items table using barcode
# Syntax: addItemByBarcode(<connection>, <donation_id>, <barcode>, <count>)
# Returns: item.id if item is successfully created, else -1
# Note: Fails if invalid donation_id or barcode. Defaults to 1 if arg count < 1 for autoscan.
def addItemByBarcode(db, did, code, count):

	if not existDonation(db, did):
		return -1

	if not existBarcode(db, code):
		return -1

	# Permit negative count for quick scanning: 1 code == 1 count
	if count < 1:
		count = 1

	# Get barcode data
	c = db.cursor()
	c.execute('''SELECT title, units FROM barcodes WHERE code = ?''', (code,))
	codeData = c.fetchone()

	# Test for matching item in table
	c.execute('''SELECT id, count FROM items WHERE did=? AND title=? AND units=?''', (did, codeData[0], codeData[1]))
	result = c.fetchone()

	# Item in table: add count to existing item
	if result is not None: 
		newCount = result[1] + count
		c.execute('''UPDATE items SET count = ?, barcode = ? WHERE id = ?''', (newCount, code, result[0]))

	# Item not in table: add new item to table
	else:
		c.execute('''INSERT INTO items(did, barcode, title, count, units) VALUES(?,?,?,?,?)''', (did, code, codeData[0], count, codeData[1]))

	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1

# Function listProviderDonations()
# Purpose: returns a list of donations by uid
# Syntax: listProviderDonations(<connection>, <provider_id>, <donation_filter)
# Returns: A list of all matching donations or an empty list if no types selected or donations found
# Note: donation filter is two bit binary selection filter s.t. 00:none, 01:pending, 10:completed, 11:both
def listProviderDonations(db, pid, types):

	c = db.cursor()

	# Case no donations
	if (0b11 & types == 0b00):
		return []

	# Case all donations
	elif (0b11 & types == 0b11):
		c.execute('''SELECT * FROM donations WHERE provider = ?''', (pid,))

	# Case pending donations
	elif (0b01 & types == 0b01):
		c.execute('''SELECT * FROM donations WHERE provider = ? AND completed = ?''', (pid, 0))

	# Case completed donations
	elif (0b10 & types == 0b10):
		c.execute('''SELECT * FROM donations WHERE provider = ? AND completed != ?''', (pid, 0))

	result = c.fetchall()
	c.close()
	return result		
	

# Function getDonationItems()
# Purpose: returns a list of items by did
# Syntax: getDonationItems(<connection>, <donation_id>)
# Returns: A list of all matching items, or an empty list if none found.
def getDonationItems(db, did):

	c = db.cursor()
	c.execute('''SELECT * from items WHERE did = ?''', (did,))
	result = c.fetchall()
	c.close()
	return result


# Function claimDonation()
# Purpose: assign a receiver to an unclaimed donation
# Syntax: claimDonation(<connection>, <donation_id>, <recevier_uid>)
# Returns: On successful update to donation receiver field returns True, else False
def claimDonation(db, did, rid):

	final = False
	c = db.cursor()
	c.execute('''SELECT receiver, completed FROM donations WHERE id = ?''', (did,))
	result = c.fetchone()

	if result is not None:
		if (result[0] == 'pending') and (result[1] == 0):
			c.execute('''UPDATE donations SET receiver = ? WHERE id = ?''', (rid, did))
			c.execute('''SELECT receiver, completed FROM donations WHERE id = ?''', (did,))
			result = c.fetchone()
			if result is not None:
				if (result[0] == rid) and (result[1] == 0):
					final = True
	db.commit
	c.close()
	return final


# Function existDonation() 
# Purpose: Check for donation in donations table
# Syntax: existDonation(<connection>, <donation_id_to_check>)
# Returns: True if donation exists / False if donation does not exist
# Note: id is primary key, so 0 and 1 are only lengths possible
def existDonation(db, did):
	
	c = db.cursor()
	c.execute('''SELECT id FROM donations WHERE id=?''', (did,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function existItem() 
# Purpose: Check for item in items table
# Syntax: existItem(<connection>, <item_id_to_check>)
# Returns: True if item exists / False if item does not exist
# Note: id is primary key, so 0 and 1 are only lengths possible
def existItem(db, iid):
	
	c = db.cursor()
	c.execute('''SELECT id FROM items WHERE id=?''', (iid,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function existBarcode() 
# Purpose: Check for barcode in barcode table
# Syntax: existBarcode(<connection>, <barcode_to_check>)
# Returns: True if barcode exists / False if barcode does not exist
# Note: code is unique column, so 0 and 1 are only lengths possible
def existBarcode(db, code):
	
	c = db.cursor()
	c.execute('''SELECT code FROM barcodes WHERE code=?''', (code,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False
