#!/usr/bin/python

import ldap
from ldap.controls import SimplePagedResultsControl
import sys
import ldap.modlist as modlist

LDAP_SERVER = "ldap://lnxadc01.the-soos.lan"
BIND_DN = "ldap_bind@the-soos.lan"
BIND_PASS = "*****"
USER_FILTER = "(&(objectClass=user)(objectCategory=person))"
USER_BASE = "ou=Medewerkers,dc=the-soos,dc=lan"
PAGE_SIZE = 10

# LDAP connection
try:
  #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
  ldap_connection = ldap.initialize(LDAP_SERVER)
  ldap_connection.simple_bind_s(BIND_DN, BIND_PASS)
except ldap.LDAPError, e:
  sys.stderr.write('Error connecting to LDAP server: ' + str(e) + '\n')
  sys.exit(1)

# Lookup usernames from LDAP via paged search
paged_results_control = SimplePagedResultsControl(
  ldap.LDAP_CONTROL_PAGE_OID, True, (PAGE_SIZE, ''))
accounts = []
pages = 0
while True:
  serverctrls = [paged_results_control]
  try:
      msgid = ldap_connection.search_ext(USER_BASE,
                                         ldap.SCOPE_ONELEVEL,
                                         USER_FILTER,
                                         attrlist=['mail',
                                                   'pager',
                                                   'sAMAccountName'],
                                         serverctrls=serverctrls)
  except ldap.LDAPError, e:
      sys.stderr.write('Error performing user paged search: ' +
                       str(e) + '\n')
      sys.exit(1)
  try:
      unused_code, results, unused_msgid, serverctrls = \
                 ldap_connection.result3(msgid)
  except ldap.LDAPError, e:
      sys.stderr.write('Error getting user paged search results: ' +
                       str(e) + '\n')
      sys.exit(1)
  for result in results:
      pages += 1
      accounts.append(result)
  cookie = None
  for serverctrl in serverctrls:
      if serverctrl.controlType == ldap.LDAP_CONTROL_PAGE_OID:
          unused_est, cookie = serverctrl.controlValue
          if cookie:
              paged_results_control.controlValue = (PAGE_SIZE, cookie)
          break
  if not cookie:
      break

# LDAP unbind
ldap_connection.unbind_s()

# Make dictionary with user data
user_map = {}
for entry in accounts:
  if entry[1].has_key('pager') and \
     entry[1].has_key('sAMAccountName'):
      user_map[entry[1]['pager'][0]] = entry[1]['sAMAccountName'][0]
