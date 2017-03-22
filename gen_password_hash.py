#!/usr/bin/python

import sys
import uuid
import hashlib
import MySQLdb


def hash_password(password,salt):
    # uuid is used to generate a random number
    #salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


# uuid is used to generate a random number
salt = uuid.uuid4().hex
print("Salt=" + salt)
new_pass = raw_input('Please enter a password: ')
hashed_password = hash_password(new_pass,salt)
pwd,slt = hashed_password.split(':')
print("Slt=" + slt)
print("pwd=" + pwd)

print('The string to store in the db is: ' + hashed_password)
old_pass = raw_input('Now please enter the password again to check: ')
if check_password(hashed_password, old_pass):
    print('You entered the right password')

    # GOAL is to generate something like below
    #-- Create default user "guacadmin" with password "guacadmin"
    #INSERT INTO guacamole_user (username, password_hash, password_salt)
    #VALUES ('guacadmin',
    #    x'CA458A7D494E3BE824F5E1E175A1556C0F8EEF2C2D7DF3633BEC4A29C4411960',  -- 'guacadmin'
    #    x'FE24ADC5E11E2B25288D1704ABE67A79E342ECC26064CE69C5B3177795A82264');

    # set othere vars
    timezone='Europe/Amsterdam'
    valid_from='2016-01-01'
    valid_until='2017-12-31'
    disabled=1
    expired=1
 # THIS IS IT -> SET @selt=UNHEX(SHA2(UUID(),256));update guacamole_user SET password_salt = @selt, password_hash = UNHEX(SHA2(CONCAT('supergeheim',HEX(@selt)), 256)) WHERE username='xxx';
    sql="insert into guacamole_db set (username,password_salted,password_hash,yubikey,disabled,expired,valid_from,valid_until,timezone) VALUES ('bladiebla',x'" + "UNHEX(" + salt.upper() + ")" + "',x'" + "UNHEX(" + hashed_password.upper() +")" + "','ccccccdddcin'," + str(disabled) + "," + str(expired) + "," + valid_from + "," + valid_until + ")"
    print(sql)

else:
    print('I am sorry but the password does not match')


sys.exit(0)


