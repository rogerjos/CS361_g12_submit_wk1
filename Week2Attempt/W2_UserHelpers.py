


#Function getOpenDonations()
#Purpose: returns a list of donations marked as not completed
#Syntax: getOpenDonations(<connection>)
#Returns: A list of all un-completed donations
def getOpenDonations(db):

        c = db.cursor()
        c.execute('''SELECT * FROM donations WHERE completed = ? ''', (0,))
        result = c.fetchall()
        c.close
        return result

#Function getReceiverDonations()
#Purpose: returns a list of donations marked as completed and with specified receiver.
#Syntax: getReceiverDonations(<connection>, rid)
#Returns: A list of donations that has the appropriate receiver ID , and marked as complete
def getReceiverDonations(db,rid):

        c = db.cursor()
        c.execute('''SELECT * FROM donations WHERE receiver = ? AND completed != ?''',(rid,0,))
        results = c.fetchall()
        c.close
        return results


#W2 User Story 1: As a receiver, I can see open donations
#Syntax: ( <test_dict>, <connection>)
def testReceiverOpenDonations(test,db):

        test['openReceiverDonations'][0] += 1
        result = getOpenDonations(db)

        #no donations found
        if result is []:
            test['openReceiverDonations'][1] += 1
            print('No opoen donations found.')

        #donations found
        else:
            print('\n\t\t\t Open Donations')
            for r in result:
                print('\nrow\tprovider\treceiver\tcreated\t\t\t\tcompleted')
                print('{0}\t{1}\t\t{2}\t\t{3}\t{4}'.format(r[0], r[1], r[2], r[3], r[4]))

#W2 User Story 2: As a receiver, I can see my past donations
#Syntax ( <test_dict>, db, receiver)
def testReceiverHistory(test,db,receiver):

        test['receiverHistory'][0] += 1
        result = getReceiverDonations(db, receiver)

        if result is []:
            test['receiverHistory'][1] +=1
            print('No past donations found.')
        else:
            print('\n\t\t\t\tPast Donations')
            for r in result:
                    print('\nrow\tprovider\treceiver\tcreated\t\t\t\tcompleted')
                    print('{0}\t{1}\t\t{2}\t\t{3}\t{4}'.format(r[0], r[1], r[2], r[3], r[4]))
