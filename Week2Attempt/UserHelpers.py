# UserHelpers.py implements helper functions for manipulating the user table

import hashlib # Hash passwords with SHA256


# Function: validUser()
# Purpose: Validate uid/pwd pair in users table
# Syntax: validUser(<connection>, <user_id_to_check>, <password to check>)
# Returns: True on valid pair / False on invalid pair
def validUser(db, uid, pwd):

	# hash pwd argument
	hash_object = hashlib.sha256(pwd.encode())
	hex_dig = hash_object.hexdigest()

	# get current hash
	c = db.cursor()
	c.execute('''SELECT hash FROM users WHERE uid=?''', (uid,))
	result = c.fetchone()
	c.close()

	# If current hash exists and matches arg hash then uid/pwd is valid
	if result is not None:
		if result[0] == hex_dig:
			return True

	# Default to uid/pwd is invalid
	return False


# Function: writeUser()
# Purpose: Write to users table, creating or updating row as necessary
# Syntax: writeUser(<connection>, <parent_id>, <child_id>, <permissions>, <pwd>)
# Returns True on success / False on failure
# Note: First user into users gets admin permissions
# Note: pwd only used for new users. changePassword will write to existing pwds
def writeUser(db, pid, uid, perms, pwd):

	# hash pwd argument
	hash_object = hashlib.sha256(pwd.encode())
	hex_dig = hash_object.hexdigest()

	# First user into table gets administrative access!
	c = db.cursor()
	c.execute('''SELECT * FROM users''')
	result = c.fetchone()
	if result is None:
		firstUser = True
		c.execute('''INSERT INTO users(pid, perms, uid, hash) VALUES(?,?,?,?)''', (pid, 0b1111, uid, hex_dig))

	# Otherwise table not empty:
	else:
		firstUser = False
		# Get parent permissions
		c.execute('''SELECT perms FROM users WHERE uid=?''', (pid,))
		result = c.fetchone()
		if result is None:
			return False
		pperms = result[0]

		# If creating admin, parent must be admin
		if (0b1000 & perms == 0b1000) and (0b1000 & pperms != 0b1000):
			return False
	
		# If creating org, parent must be admin
		if (0b100 & perms == 0b100) and (0b1000 & pperms != 0b1000):
			return False

		# Assigned child roles must be enabled in parent some role must be assigned
		if (0b1 & perms != 0b1 & pperms) and (0b10 & perms != 0b10 & pperms) or (0b0011 & perms == 0):
			return False

		# Get pid and confirm ownership
		c.execute('''SELECT pid FROM users WHERE uid=?''', (uid,))
		result = c.fetchone()
	
		# If user does not exist, create and add hash
		if result is None:
			c.execute('''INSERT INTO users(pid, perms, uid, hash) VALUES(?,?,?,?)''', (pid, perms, uid, hex_dig))

		# If user exists and pid owns user, update all but hash
		elif (result is not None) and (result[0] == pid):
			# update user
			c.execute('''UPDATE users SET perms = ? WHERE uid = ?''', (perms, uid))		

	# test for success
	c.execute('''SELECT perms FROM users WHERE uid=?''', (uid,))
	result = c.fetchone()
	db.commit()
	c.close()

	# If user exists...
	if result is not None:
		# First user with full access: True
		if (firstUser is True) and (result[0] == 0b1111):
			return True
		# Subsequent user with matching access: True
		elif result[0] == perms:
			return True
	
	# Neither case above pertains: False
	return False
