import datetime
from Schema import createSchema
from UserHelpers import validUser, writeUser
from DonationHelpers import addBarcode, addDonation, addItemByManual, addItemByBarcode, listProviderDonations, getDonationItems, claimDonation 


# populate users fills the users table
def populateUsers(db, parents, users, perms, pwd):

	# Build user table against params
	for ppid, uid, perm, wd in zip(parents, users, perms, pwd):
		writeUser(db, ppid, uid, perm, wd)

# prints user table
def printUserTable(db):

	print('\n\t\tUser Table\n')
	c.execute('''SELECT pid, perms, uid, hash FROM users''')
	all_rows = c.fetchall()
	print('pid\tperm\tuid\thash')
	for row in all_rows:
		print('{0}\t{1:04b}\t{2}\t{3}'.format(row[0], row[1], row[2], row[3]))


# populateBarcodes fills the barcodes table
def populateBarcodes(db, barcodes):

	for row in barcodes:
		addBarcode(db, row[0], row[1], row[2])


# Story 1: As a user I can log onto my organization's account
# Syntax: (<test_dict>, <connection>, <user_list>, <pwd_list>, <bool_expected>)
def testLogOn(test, db, users, pwds, expected):

	print('')

	# Step though parameter lists
	for user, pwd in zip(users, pwds):
		# Test validity and print result
		result = validUser(db, user, pwd)
		print('{0}:{1} validates to {2}. Expected {3}'.format(user, pwd, result, expected))
		# Increment test count
		test['validUser'][0] += 1
		# If result not expected, increment failure count
		if result != expected:
			test['validUser'][1] += 1


# Story 2: As a provider I can add a donation item manually
# Syntax: (<test_dict>, <connection>, <provider_uid>, <item_val_list>)	
def testManItem(test, db, provider, items):

	# Create a new donation
	test['addDonation'][0] += 1
	did = addDonation(db, provider, None)
	if did == -1:
		test['addDonation'][1] += 1

	# Create new items in donation
	print('\nAdding items to donation {0} by value.'.format(did))			
	for i in items:
		test['addItemByManual'][0] += 1
		result = addItemByManual(db, did, i[1], i[3], i[2])
		if result < 1: # If add failed
			test['addItemByManual'][0] += 1

	# Print status. Will show items in "view" stories
	print('Added {0} items to donation {1}'.format((test['addItemByManual'][0] - test['addItemByManual'][1]), did))


# Story 3: As a provider I can add a donation item via barcode
# Syntax: (<test_dict>, <connection>, <provider_uid>, <item_bar_list>)	
def testBarItem(test, db, provider, items):

	# Create a new donation
	test['addDonation'][0] += 1
	did = addDonation(db, provider, None)
	if did == -1:
		test['addDonation'][1] += 1

	# Create new items in donation
	print('\nAdding items to donation {0} by barcode.'.format(did))			
	for i in items:
		test['addItemByBarcode'][0] += 1
		result = addItemByBarcode(db, did, i[0], i[3])
		if result < 1: # If add failed
			test['addItemByBarcode'][0] += 1

	# Print status. Will show items in "view" stories
	print('Added {0} items to donation {1}'.format((test['addItemByBarcode'][0] - test['addItemByBarcode'][1]), did))


# Story 4: As a provider I can view my pending donation packages
# Syntax: (<test_dict>, <connection>, <provider_uid>)	
def	showProviderPending(test, db, provider):

	# Test listProviderDonations pending
	test['listProviderDonations'][0] += 1
	result = listProviderDonations(db, provider, 0b01)

	# if no donations found
	if result is []:
		test['listProviderDonations'][1] += 1
		print('No pending donations found for provider: {0}', format(provider))

	# if donation found
	else:
		# Show donations
		print('\n\t\t\t\tPending Donations')
		for r in result:
			print('\nrow\tprovider\treceiver\tcreated\t\t\t\tcompleted')
			print('{0}\t{1}\t\t{2}\t\t{3}\t{4}'.format(r[0], r[1], r[2], r[3], r[4]))
	
			# Get items for current donation
			test['getDonationItems'][0] += 1
			items = getDonationItems(db, r[0])

			# If no items found
			if items is []:
				test['getDonationItems'][1] += 1
				print('No items found for donation: r[0]')

			# If items found
			else:
				print('\nItems in donation {0}:\niid\tdid\tbarcode\ttitle\t\tcount\tunits'.format(r[0]))
				for i in items:
					for j in i:
						print('{0}\t'.format(j), end='')
					print('')					


# Story 6: As a receiver I can claim a donation
# Syntax: (<test_dict>, <connection>, <provider_uid>, <receiver_uid>)	
def claimFirst(test, db, provider, receiver):

	# Get pending donations belonging to provider
	test['listProviderDonations'][0] += 1
	dList = listProviderDonations(db, provider, 0b01)

	# if no donations found
	if dList is []:
		test['listProviderDonations'][1] += 1
		print('No pending donations found for provider: {0}. Aborting.', format(provider))
		return

	# Test claimDonation
	test['claimDonation'][0] += 1
	if claimDonation(db, dList[0][0], receiver) is False:
		test['claimDonation'][0] += 1
		print('IT\'s FALSE SON')
	else:
		print('\n{0} claimed pending donation {1} belonging to {2}'.format(receiver, dList[0][0], provider))

# Story 5: As a provider I can view my past donations
# Syntax: (<connection>, <provider_uid>)	
# Purpose: Sets completed value for first pending donation found to now()
def completeFirst(db, provider):
	
	# Get pending donations belonging to provider
	test['listProviderDonations'][0] += 1
	dList = listProviderDonations(db, provider, 0b01)

	# if no donations found
	if dList is []:
		test['listProviderDonations'][1] += 1
		print('No pending donations found for provider: {0}. Aborting.', format(provider))
		return

	# Set completed for first donation to now
	c = db.cursor()
	c.execute('''UPDATE donations SET completed = ? WHERE id = ?''', (datetime.datetime.now(), dList[0][0]))
	db.commit
	c.close()


# Syntax: <test_dict>, (<connection>, <provider_uid>)	
def	showProviderPast(test, db, provider):

	# Test listProviderDonations past
	test['listProviderDonations'][0] += 1
	result = listProviderDonations(db, provider, 0b10)

	# if no donations found
	if result is []:
		test['listProviderDonations'][1] += 1
		print('No past donations found for provider: {0}', format(provider))

	# if donation found
	else:
		# Show donations
		print('\n\t\t\t\tPast Donations')
		for r in result:
			print('\nrow\tprovider\treceiver\tcreated\t\t\t\tcompleted')
			print('{0}\t{1}\t\t{2}\t\t{3}\t{4}'.format(r[0], r[1], r[2], r[3], r[4]))
	
			# Get items for current donation
			test['getDonationItems'][0] += 1
			items = getDonationItems(db, r[0])

			# If no items found
			if items is []:
				test['getDonationItems'][1] += 1
				print('No items found for donation: r[0]')

			# If items found
			else:
				print('\nItems in donation {0}:\niid\tdid\tbarcode\t\ttitle\t\tcount\tunits'.format(r[0]))
				for i in items:
					for j in i:
						print('{0}\t'.format(j), end='')
					print('')					

def printHeader(header):
	eq = "=" * 80
	print('\n{0}\n\t{1}\n{0}'.format(eq, header))

def printResults(test):
	print('')
	for key in test:
		if test[key][0] > 0:
			if test[key][1] > 0:
				print('FAIL: {0} failed {1} of {2} tests.'.format(key, test[key][1], test[key][0]))
			else:
				print('PASS: {0} passed all {1} tests'.format(key, test[key][0]))


if __name__ == '__main__':

	# Section headers/stories
	stories = [
		'INITIALIZATION COMPLETE',
		'STORY 1: AS A USER I CAN LOG ONTO MY ORGANIZATION\'S ACCOUNT', 
		'STORY 2: AS A PROVIDER I CAN ADD A DONATION ITEM MANUALLY', 
		'STORY 3: AS A PROVIDER I CAN ADD A DONATION ITEM VIA BARCODE', 
		'STORY 4: AS A PROVIDER I CAN VIEW MY PENDING DONATION PACKAGES', 
		'STORY 5: AS A PROVIDER I CAN VIEW MY PAST DONATIONS', 
		'STORY 6: AS A RECEIVER I CAN CLAIM A DONATION',
		'FUNCTION TEST RESULTS'
	]

	# key is function, value is [test_count, failure_count]
	test = dict() # For test results
	test['validUser'] = [0, 0]
	test['addDonation'] = [0, 0]
	test['addItemByManual'] = [0, 0]
	test['addItemByBarcode'] = [0, 0]
	test['listProviderDonations'] = [0, 0]
	test['getDonationItems'] = [0, 0]
	test['claimDonation'] = [0, 0]

	# Initialization values for users table
	parents = ['admin', 'admin', 'admin','P_Org', 'R_Org'] # Parent IDs
	users0 = ['admin', 'P_Org', 'R_Org', 'Pearl', 'Ruby'] # User IDs
	users1 = ['badmin', 'O_Org', 'Q_Org', 'Opal', 'Quartz'] # User IDs
	perms = [0b1111, 0b0110, 0b0101, 0b0010, 0b0001] # Permission bits
	pwd0 = ['admin', 'alice', 'bob', 'carol', 'david'] # Passwords
	pwd1 = ['nimda', 'olive', 'rob', 'hunter2', 'avery'] # More passwords

	# Intialization values item and barcodes
	items = [
		['111111111111', 'organic kumqat', 'each', 32], 
		['222222222222', 'hot peppers', 'lb', 16], 
		['333333333333', 'PBR lager', 'case', 8], 
		['444444444444', 'ground beef', 'lb', 4], 
		['555555555555', 'ground cumin', 'oz', 2], 
		['666666666666', 'B1 steak sauce', 'bottle', 1]
	]

	# Generate tables
	db = createSchema()
	c = db.cursor()

	# Populate users table
	populateUsers(db, parents, users0, perms, pwd0)
	populateUsers(db, parents, users1, perms, pwd1)
	printHeader(stories[0])
	printUserTable(db)

	# Populate barcodes table
	populateBarcodes(db, items)

	printHeader(stories[1])
	testLogOn(test, db, users0, pwd0, True)
	testLogOn(test, db, users0, pwd1, False)
	testLogOn(test, db, users1, pwd1, True)
	testLogOn(test, db, users1, pwd0, False)

	printHeader(stories[2])
	testManItem(test, db, users0[3], items)	

	printHeader(stories[3])
	testBarItem(test, db, users1[3], items)	

	printHeader(stories[4])
	showProviderPending(test, db, users0[3])

	printHeader(stories[6])
	claimFirst(test, db, users1[3], users1[4])

	printHeader(stories[5])
	completeFirst(db, users1[3])
	showProviderPast(test, db, users1[3])

	# Show test results
	printHeader(stories[7])
	printResults(test)

	c.close()
	db.close()
