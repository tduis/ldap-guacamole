#!/usr/bin/python
# Author: t.duis <t.duis@e-genius.nl>
# Date:   21-11-2016
#
# Goal:
# Query a (samba4) Active Directory and read the sAMAccount and pager field, the last contains yubikey-id (first 12 chars of output)
#
# Requirements: 
# - install ldap support (yum install python-ldap) 
# - install mysql support (yum install MySQL-python)

import sys, getopt
import ldap
import MySQLdb


# Function to get the yubikey for the 'username' in database
# parameters: <todo>
#
def mysql_check_yubikey(username, conn_host, conn_usr, conn_pwd, conn_db):

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

   print("Found for user %s, yubikey ( %s )" % username, data)

   # disconnect from server
   db.close()

   # Give back the results (count)
   return data 


# Function to check if a user in the mysql db is present
# Parameters: <todo>
#
def guacamole_check_user(username, conn_host, conn_usr, conn_pwd, conn_db):

   # Open database connection
   db = MySQLdb.connect(conn_host, conn_usr, conn_pwd, conn_db )

   # prepare a cursor object using cursor() method
   cursor = db.cursor()

   # execute SQL query using execute() method.
   sql = "SELECT count(username) FROM guacamole_user WHERE username='" + username + "'"
   cursor.execute(sql)

   # Fetch a single row using fetchone() method.
   data = cursor.fetchone()


   # disconnect from server
   db.close()

   # Lets return the results to calling....
   return data

def ShowUsage(error):
   if error != "":
      print "\nError: " + str(error) + "\n\n"
   print "\n\nUsage:"
   print "--------------------------------------------"
   print "sync-yubikey -s <ldap-server> -u <username> -p <password> -m <mysql_host> -c <db_user> -d <mysql_db> -e <db_user_pwd>"
   print "or:"
   print "sync-yubikey -server <ldap-server> --usr <username> --pwd <password> --conn_host <mysql_host> --conn_usr <db_user> --conn_db <mysql_db> --conn_pwd <db_user_pwd>"
   print "\n\n"
   sys.exit()


def main(argv):
   server = ''
   usr = ''
   pwd = ''
   conn_host = ''
   conn_usr = ''
   conn_pwd = ''
   conn_db = ''

   debugging = "true"
   #filter = "(&(objectCategory=person)(objectClass=user))"
   #filter = "(CN=*"
   searchFilter = "(&(ObjectClass=person)(CN=*))"
   baseDN = "ou=Medewerkers, dc=the-soos, dc=lan"
   searchScope = ldap.SCOPE_SUBTREE
   retrieve_attributes = None
   try:
      opts, args = getopt.getopt(argv,"hs:u:p:m:c:d:e:",["server","usr","pwd","conn_host","conn_usr","conn_pwd","conn_db"])
   except getopt.GetoptError, e:
      ShowUsage(e)

   for opt, arg in opts:
      if opt == '-h':
         ShowUsage("")
      elif opt in ("-s", "--server"):
         server = arg
      elif opt in ("-u", "--user"):
         usr = arg
      elif opt in ("-p", "--password"):
         pwd = arg
      elif opt in ("-m", "--conn_host"):
         conn_host = arg
      elif opt in ("-c", "--conn_usr"):
         conn_usr = arg
      elif opt in ("-d", "--conn_db"):
         conn_db = arg
      elif opt in ("-e", "--conn_pwd"):
         conn_pwd = arg


   # Show (debug) output
   if debugging == "true":
      print 'Serve  r = ', str(server)
      print 'Username = ', str(usr)
      print 'Password = ', str(pwd)
      print 'MySQL host   = ', str(conn_host)
      print 'MySQL user   = ', str(conn_usr)
      print 'MySQL passwd = ', str(conn_pwd)
      print 'MySQL DB     = ', str(conn_db)

        

   # Open a connection
   try: 
      # Make/open connection
      l = ldap.open(server)

      # Searching doesn't require a bind in LDAP v3.
      l.protocol_version = ldap.VERSION3

      # Do a authenticated bind
      l.simple_bind_s(usr, pwd)

      # Debug logging
      if debugging == "true":
         print("Successfully bind to server (%s)" % server)

      # Call search function
      my_search(l, baseDB, searchScope, searchFilter, retrieve_attributes)

   except ldap.LDAPError, e:

      print("Error binding: %s" % str(e))

      # handle error however you like
      l.unbind_s()
      sys.exit(2)

   # Clear the binding
   l.unbind_s()


def my_search(l, baseDN, searchScope, searchFilter, retrieveAttributes):
   print "------------------------------------"
   print("Searching..\n")
   print "Filter: %s" % searchFilter
   print "BaseDN: %s" % baseDN
   print "Scope: %s" % searchScope
   print "Attributes %s" % retrieveAttributes
   print "------------------------------------"
  

   count = 0
   result_set = []
   timeout = 0

   #(&(objectCategory=person)(objectClass=user)
   try:
      result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
      while 1:
         result_type, result_data = l.result(result_id, 0)
         if (result_data == []):
            print "breaking..."
            print result_type
            print ldap.RES_SEARCH_ENTRY
            break
         else:
            if result_type == ldap.RES_SEARCH_ENTRY:
               result_set.append(result_data)


      if len(result_set) == 0:
         print "No Results."
         return
      for i in range(len(result_set)):
         for entry in result_set[i]:
            try:
                if mail in entry[0]:
                   email = entry[1]['mail'][0]
                if name in entry[0]:
                   name = entry[1]['cn'][0]
                if pager in entry[0]: 
                   yubikey = entry[1]['pager'][0]
                if sAMAccountName in entry[0]:
                   loginname = entry[1]['sAMAccountName'][0]

                print "%d.\nName: %s,\nEmail: %s\nLoginName: %s\nYubikey: %s" (count, name,email,loginname, yubikey)
            except:
                pass

   except ldap.LDAPError, error_message:
      print error_message


if __name__ == "__main__":
    main(sys.argv[1:])
