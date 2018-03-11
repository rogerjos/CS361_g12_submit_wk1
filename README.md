StoriesWeekOne.py contains a demonstration of this week's user stories written in Pyton 3 which depends upon code in Schema.py, UserHelpers.py, and DonationHelpers.py. 

Run with "python3 StoriesWeekOne.py"

Schema.py contains a sqlite3 implementation of the following tables: 
	users(pid, perms, uid, hash) 
	donations(id, provider, receiver, created, completed) 
	items(id, did, barcode, title, count, units)
	barcodes(code, title, units)

UserHelpers.py contains the following user-level functions: 
	validUser() - Validates a user/pass pair
	writeUser() - Writes to user table, creating or updating a user account

DonationHelpers.py contains the following donation-level functions:
	addBarcode() adds a new barcode to the barcodes table 
	addDonation() creates a new empty donation 
	addItemByManual() adds a new item to the items table with manual values 
	addItemByBarcode() adds a new item to the items table pulling barcode data 
	listProviderDonations() lists pending and/or past donations
	getDonationItems() returns all items in a donation by donation id 
	claimDonation() updates donation.receiver value 
