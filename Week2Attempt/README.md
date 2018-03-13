W2_UserHelpers.py contains receiver specific functions, Did not want to add them to the main document for clarity sake.

StoriesWeekone.py:
	Imports the W2_UserHelpers functions in
	Added Test_8 and Test_9 to test the 2 user stories hopefully its accurately doing it.
	
getOpenDonations():
	Pulls any donations in the table that hasn't been updated with a timestamp i.e. still open

getReceiverDonations():
	Pulls donation packages specific to a receiver_uid (rid), AND has its package marked as completed (i.e. not 0)
	

