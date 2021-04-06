'''
Authors:
    Alec Dudley-Bestow, z5260201

Date:
    26 March 2021
'''

import json
import re
from src.error import AccessError, InputError
from src.auth import check_token, check_u_id, get_data, write_data, \
    valid_email, valid_name, email_taken, handle_taken

#checks if a given handle is of a valid type
def valid_handle(handle_str):
    return 3 <= len(handle_str) <= 20 and not bool(re.search(handle_str, r"[-@]"))

#returns the correct information from a user
def get_user_dictionary(user):
    return {
        'u_id': user['u_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
    }

def user_profile(token, u_id):
    '''
        returns a dictionary of information on a given user

    Arguments:
        token (jwt)    - authorization token
        u_id (integer)    - specifies the target user

    Exceptions:
        InputError  - Occurs when the given u_id is invalid
        AccessError - Occurs when the token given is invalid

    Return Value:
        Returns user dictionary
    '''
    check_token(token)
    user_index = check_u_id(u_id, True)
    data = get_data()
    
    return get_user_dictionary(data['users'][user_index])

def users_all(token):
    '''
        returns a list of dictionaries of information on all users

    Arguments:
        token (jwt)    - authorization token

    Exceptions:
        AccessError - Occurs when the token given is invalid

    Return Value:
        Returns a list of user dictionaries
    '''
    check_token(token)
    user_list = []
    data = get_data()
    for user in data['users']:
        user_list.append(get_user_dictionary(user))
    return {'users' : user_list}

def user_profile_setname(token, name_first, name_last):
    '''
        changes a users name in the database

    Arguments:
        token (jwt)    - authorization token
        name_first (string)    - the new first name
        name_last (string)    - the new last name

    Exceptions:
        InputError  - Occurs when either name isn't between 1 and 50 characters
        AccessError - Occurs when the token given is invalid

    Return Value:
        Returns empty dictionary
    '''
    user_index = check_token(token)
    if not valid_name(name_first):
        raise InputError(description=\
            'name_first is not between 1 and 50 characters inclusively in length')
    elif not valid_name(name_last):
        raise InputError(description=\
            'name_last is not between 1 and 50 characters inclusively in length')
    else:
        data = get_data()
        data['users'][user_index]['name_first'] = name_first
        data['users'][user_index]['name_last'] = name_last
        write_data(data)
        
    return {}

def user_profile_setemail(token, email):
    '''
        changes a users email address in the database

    Arguments:
        token (jwt)    - authorization token
        email (string)    - the new email address

    Exceptions:
        InputError  - Occurs when the given email address is of invalid format
        InputError  - Occurs when the given email address is already taken
        AccessError - Occurs when the token given is invalid

    Return Value:
        Returns empty dictionary
    '''
    user_index = check_token(token)
    if not valid_email(email):
        raise InputError(description=\
            'Email entered is not a valid email')
    elif email_taken(email):
        raise InputError(description=\
            'Email address is already being used by another user')
    else:
        data = get_data()
        data['users'][user_index]['email'] = email
        write_data(data)
        
    return {}

def user_profile_sethandle(token, handle_str):
    '''
        changes the user handle of a person in the database

    Arguments:
        token (jwt)    - authorization token
        name_first (string)    - the new first name
        
    Exceptions:
        InputError  - Occurs when the new handle contains an 
                      @ symbol or isn't between 3 and 20 characters
        InputError  - Occurs when the given handle is already taken
        AccessError - Occurs when the token given is invalid

    Return Value:
        Returns empty dictionary
    '''
    user_index = check_token(token)
    if not valid_handle(handle_str):
        raise InputError(description=\
            'Handle is not valid')
    elif handle_taken(handle_str):
        raise InputError(description=\
            'Handle is already used by another user')
    else:
        data = get_data()
        data['users'][user_index]['handle_str'] = handle_str
        write_data(data)
        
    return {}
