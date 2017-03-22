#!/usr/bin/python

import ldap
import sys
import uuid
import hashlib
import binascii

# MySQL functions
import MySQLdb


# Function to generate the salt via MySQL
def gen_mysql_salt(conn_host,conn_usr,conn_pwd,conn_db):
   try:
      # Open database connection
      db = MySQLdb.connect(conn_host,conn_usr,conn_pwd,conn_db)

      # Lets generate the salt in/via mysql
      salt_sql="SELECT UNHEX(SHA2(UUID(),256)) as salt"

      # prepare a cursor object using cursor() method
      cursor = db.cursor()

      # execute SQL query using execute() method.
      cursor.execute(salt_sql)

      # Fetch a single row using fetchone() method.
      data = cursor.fetchone()

      # Close the database connection
      db.close()

      # Return the salt
      return data[0]

   except:
      print("Error trying to generate salt: %s" % conn_db)


# Function to add a user with password to guacamole_db
def mysql_add_guacamole_usr(username, password, yubikey, conn_host, conn_usr, conn_pwd, conn_db):

   # Go get the salt
   salt = gen_mysql_salt(conn_host, conn_usr, conn_pwd, conn_db) 
   print( salt )




   # THIS IS IT -> SET @selt=UNHEX(SHA2(UUID(),256));update guacamole_user SET password_salt = @selt, password_hash = UNHEX(SHA2(CONCAT('geheim',HEX(@selt)), 256)) WHERE username='admtduis';

   # SET othere parameters
   timezone='Europe/Amsterdam'
   valid_from='2016-01-01'
   valid_until='2017-12-31'
   disabled=0
   expired=1

   # Lets store the salt as a HEXIFIED value
   salt_hex=binascii.hexlify(salt)

   print("salt:" + salt.upper())
   print "Password: " + password
   print "yubikey: " + yubikey
   print "disabled: " + str(disabled)
   print "expired: " + str(expired)

   # Build the SQL to use for inserting a user in the DB. NOTE THE USER IS ENABLED by default
   sql="INSERT INTO guacamole_user (username,password_salt,password_hash,yubikey,disabled,expired,valid_from,valid_until,timezone) VALUES ('" + username + "',UNHEX('" + salt_hex.upper() + "'),UNHEX(SHA2(CONCAT('" + password + "','" + salt_hex.upper() + "'),256)),'" + yubikey + "'," + str(disabled) + "," + str(expired) + ",'" + valid_from + "','" + valid_until + "','" + timezone + "')"

   # debugging
   print(sql)
   try:
      # Open database connection
      db = MySQLdb.connect(conn_host,conn_usr,conn_pwd,conn_db)

      # TODO, werkt niet
      cursor = db.cursor()

      # Execute the sql statement
      cursor.execute(sql)


      # NOTE:
      # password_salt = UNHEX(salt)@selt, password_hash = UNHEX(SHA2(CONCAT('geheim',HEX(@selt)), 256)) WHERE username='admtduis';

      # Close the database connection
      db.close()

   except:
      print("Error opening database: %s" % conn_db)

# ------------------------------------------------------------------
# Function to get the yubikey for the 'username' in database
def mysql_get_yubikey(username, conn_host, conn_usr, conn_pwd, conn_db):
   print "Inside mysql_get_yubikey()"
   # Open database connection
   db = MySQLdb.connect(conn_host,conn_usr,conn_pwd,conn_db)

   # prepare a cursor object using cursor() method
   cursor = db.cursor()

   # execute SQL query using execute() method.
   sql = "SELECT yubikey FROM guacamole_user WHERE username='" + username + "'"
   print(sql)
   cursor.execute(sql)

   # Fetch a single row using fetchone() method.
   data = cursor.fetchone()

   print("Found for user %s, yubikey ( %s )" % (username, data[0]))

   # disconnect from server
   db.close()

   # Give back the results (count)
   return str(data[0]);

# ------------------------------------------------------------------
# Function to count the existing 'username' in database
# Parameters: 
# - username   : The username we are looking for in mysql
# - conn_host  : The (MySQL) hostname/ip
# - conn_usr   : the (MySQL) user credentials to connect to database
# - conn_pwd   : The (MySQL) password credentials to connect to database
# - conn_db    : The (MySQL) database name to query against
#
def mysql_check_user(username, conn_host, conn_usr, conn_pwd, conn_db):

   # Open database connection
   db = MySQLdb.connect(conn_host,conn_usr,conn_pwd,conn_db)

   # prepare a cursor object using cursor() method
   cursor = db.cursor()

   # execute SQL query using execute() method.
   sql = "SELECT COUNT(*) as aantal FROM guacamole_user WHERE username='" + username + "'"
   print(sql)
   cursor.execute(sql)

   # Fetch a single row using fetchone() method.
   data = cursor.fetchone()

   print("Found %s user(s) with that name" % data)

   # disconnect from server
   db.close()

   # Give back the results (count)
   return data[0];


# ------------------------------------------------------------------
def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
# ------------------------------------------------------------------
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
 
#new_pass = raw_input('Please enter a password: ')
#hashed_password = hash_password(new_pass)
#print('The string to store in the db is: ' + hashed_password)
#old_pass = raw_input('Now please enter the password again to check: ')
#if check_password(hashed_password, old_pass):
#    print('You entered the right password')
#else:
#    print('I am sorry but the password does not match')

#print("insert into guacamole_db set username,password_salted,password_hash values ('admtduis','%s','%s');" % salt password)
#sys.exit(0)

## first you must open a connection to the server
try:
	l = ldap.open("172.20.99.10")
	## searching doesn't require a bind in LDAP V3.  If you're using LDAP v2, set the next line appropriately
	## and do a bind as shown in the above example.
	# you can also set this to ldap.VERSION2 if you're using a v2 directory
	# you should  set the next option to ldap.VERSION2 if you're using a v2 directory
	l.protocol_version = ldap.VERSION3	
        l.simple_bind_s('administrator@the-soos.lan', '**********')

except ldap.LDAPError, e:
	print e
	# handle error however you like


## The next lines will also need to be changed to support your search requirements and directory
baseDN = "ou=Medewerkers,dc=the-soos,dc=lan"
searchScope = ldap.SCOPE_SUBTREE
## retrieve all attributes - again adjust to your needs - see documentation for more options
retrieveAttributes = None 
searchFilter = "(&(ObjectClass=person)(CN=*))"

try:
	ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
	result_set = []
	while 1:
		result_type, result_data = l.result(ldap_result_id, 0)
		if (result_data == []):
                        print "breaking"
			break
		else:
			## here you don't have to append to a list
			## you could do whatever you want with the individual entry
			## The appending to list is just for illustration. 
			if result_type == ldap.RES_SEARCH_ENTRY:
				result_set.append(result_data)
	#print result_set
        print "Items found: ", len(result_set)

        if len(result_set) == 0:
           print "No Results."
           sys.exit(1)

        # Loop over results from ldap
        for i in range(len(result_set)):
           print "item: ", i
           for entry in result_set[i]:
              # this will result in something like:
              print "----------------------------"
              print entry
              print "----------------------------"
              mydict=entry[1]
              if 'pager' in mydict:
                 print entry[1]['sAMAccountName'][0]
                 print entry[1]['pager'][0]
                 loginname = entry[1]['sAMAccountName'][0]
                 yubikey = entry[1]['pager'][0]

                 # Now we can check mysql for existence of username in tabel guacamole_db.guacamole_user
                 result = mysql_check_user(loginname, 'localhost','root','*******','guacamole_db')
                 print result
                 if result == 1:
                    # Now we have a user that is present in DB, lets check the yubikey
                    db_yubikey=mysql_get_yubikey(loginname, 'localhost','root','*******!','guacamole_db')
                    if db_yubikey == yubikey:
                       print "Correct yubikey (%s)present in DB!" % db_yubikey
                    else:
                       print "We need to update the yubikey in DB!!"                 
                 else:
                    print("We need to add a user to guacamole with the name:" + loginname)
                    mysql_add_guacamole_usr(loginname,'********', yubikey,'localhost','root','*******','guacamole_db')
                    #username, password, yubikey, conn_host, conn_usr, conn_pwd, conn_db):


#              try:
#                 loginname = entry[1]['sAMAccountName'][0]
#                 yubikey = entry[1]['pager'][0]
#                 count = count + 1
#                 print "%d.\nName: %s,\nEmail: %s\nLoginName: %s\nYubikey: %s" (count, name,email,loginname, yubikey)
#              except:
#                 pass
           

except ldap.LDAPError, e:
	print e
