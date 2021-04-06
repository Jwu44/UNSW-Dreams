'''
Authors: 
    Justin Wu, z5316037
    Dionne So, z5310329

Date: 31 March 2021
'''

import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from http_tests.channels_http_test import register_users, users, channels_create

ACCESS_ERROR = 403
INPUT_ERROR = 400

REGISTER = 'auth/register/v2'
DM_CREATE = 'dm/create/v1'
DM_INVITE = 'dm/invite/v1'
DM_DETAILS = 'dm/details/v1'
USER_PROFILE = '/user/profile/v2'

# --------------------------------------------------------------------------------------- #
# ----------------------------- Fixtures for Dm Functions ------------------------------- #
# --------------------------------------------------------------------------------------- #
@pytest.fixture
def spare_users():
    '''
    These are some extra users in additon
    to the 'users' fixture.
    '''
    user3 = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'MarcChee@gmail.com',
        'password': 'asldfkj34kj',
        'name_first': 'Marc' ,
        'name_last': 'Chee',
    }).json()

    user4 = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'HaydenSmith@gmail.com',
        'password': 'x384sdmfn34kj',
        'name_first': 'Hayden' ,
        'name_last': 'Smith',
    }).json()

    return (user3, user4)

@pytest.fixture
def dms_create(users, spare_users):
    '''
    Setting up 2 dms:
        - Dm from User1 to User2
        - Dm from User2 to User1 & User3 
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, _ = spare_users

    dm1 = requests.post(config.url + 'dm/create/v1', json = {
        'token': user1['token'],
        'u_ids': [user2['auth_user_id']]
    }).json()

    dm2 = requests.post(config.url + 'dm/create/v1', json = {
        'token': user2['token'],
        'u_ids': [user1['auth_user_id'], user3['auth_user_id']]
    }).json()
    
    return {
        'dm1': dm1,
        'dm2': dm2,
    }

@pytest.fixture
def dm_details(users, spare_users, dms_create):
    '''
    Returns the expected dm details for dm1 and dm2.
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, user4 = spare_users

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    dm1_details = {
        'name': dm1['dm_name'],
        'members': [
            {
                'u_id': user1['auth_user_id']
            },
            {
                'u_id': user2['auth_user_id']
            }
        ]
    }

    dm1_invite_details = {
        'name': dm1['dm_name'],
        'members': [
            {
                'u_id': user1['auth_user_id']
            },
            {
                'u_id': user2['auth_user_id']
            },
            {
                'u_id': user3['auth_user_id']
            }
        ]
    }

    dm2_details = {
        'name': dm2['dm_name'],
        'members': [
            {
                'u_id': user2['auth_user_id']
            },
            {
                'u_id': user1['auth_user_id']
            },
            {
                'u_id': user3['auth_user_id']
            }
        ]
    }

    dm2_invite_details = {
        'name': dm2['dm_name'],
        'members': [
            {
                'u_id': user2['auth_user_id']
            },
            {
                'u_id': user1['auth_user_id']
            },
            {
                'u_id': user3['auth_user_id']
            },
            {
                'u_id': user4['auth_user_id']
            }
        ]
    }
    return {
        'dm1_details': dm1_details,
        'dm2_details': dm2_details,
        'dm1_invite': dm1_invite_details,
        'dm2_invite': dm2_invite_details
    }

@pytest.fixture
def list_dms(dms_create):
    '''
    Returns the expected list of dms for all registered users.
    '''
    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    user1_dms = {
        'dms': [
            {
                'dm_id': dm1['dm_id'],
                'dm_name': dm1['dm_name']
            },
            {
                'dm_id': dm2['dm_id'],
                'dm_name': dm2['dm_name']
            }
        ]
    }

    user2_dms = {
        'dms': [
            {
                'dm_id': dm1['dm_id'],
                'dm_name': dm1['dm_name']
            },
            {
                'dm_id': dm2['dm_id'],
                'dm_name': dm2['dm_name']
            }
        ]
    }

    user3_dms = {
        'dms': [
            {
                'dm_id': dm2['dm_id'],
                'dm_name': dm2['dm_name']
            }
        ]
    }

    user4_dms = {
        'dms': []
    }

    return (user1_dms, user2_dms, user3_dms, user4_dms)

@pytest.fixture
def invalid_input(users, spare_users, dms_create):
    user1 = users['user1']
    user2 = users['user2']
    user3, user4 = spare_users

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']
    return{
        'invalid_input1': {
            'token': user2['token'],
            'dm_id': 10,
            'u_id': user2['auth_user_id']
        },
        'invalid_input2': {
            'token': user2['token'],
            'dm_id': 2,
            'u_id': user2['auth_user_id']
        },
        'invalid_input3': {
            'token': user2['token'],
            'dm_id': -1,
            'u_id': user2['auth_user_id']
        },
        'invalid_input4': {
            'token': user1['token'],
            'dm_id': dm1['dm_id'],
            'u_id': 20
        },
        'invalid_input5': {
            'token': user1['token'],
            'dm_id': dm2['dm_id'],
            'u_id': 10
        },
        'invalid_input6': {
            'token': user1['token'],
            'dm_id': dm1['dm_id'],
            'u_id': 5
        },
        
    }

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Dm Create --------------------------------------- #
# --------------------------------------------------------------------------------------- #
def test_dm_create(dms_create):
    '''
    Tests the intended behaviour of dm create with
    correct dm_id and dm_name output.
    '''
    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    assert dm1['dm_id'] == 1
    assert dm2['dm_id'] == 2
    assert dm1['dm_name'] == 'authuser,firstlast'
    assert dm2['dm_name'] == 'authuser,firstlast,marcchee'

def test_dm_create_input_error(users, dms_create):
    '''
    Tests for InputError when u_id does not refer to a valid user.
    '''
    user1 = users['user1']
    user2 = users['user2']

    invalid_input1 = {
        'token': user1['token'],
        'u_ids': [100, 101, 102]
    }

    invalid_input2 = {
        'token': user2['token'],
        'u_ids': [-97, -98, -99]
    }

    assert requests.post(config.url + 'dm/create/v1', json=invalid_input1).status_code == INPUT_ERROR
    assert requests.post(config.url + 'dm/create/v1', json=invalid_input2).status_code == INPUT_ERROR

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Dm Details -------------------------------------- #
# --------------------------------------------------------------------------------------- #
def check_dm_details(user, dm, dm_detail):
    assert requests.get(config.url + 'dm/details/v1', \
        params={'token': user['token'], 'dm_id': dm['dm_id']}).json() == dm_detail

def test_dm_details(users, spare_users, dms_create, dm_details):
    '''
    Tests the intended behaviour of dm details with
    correct name and members output.
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, _ = spare_users

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    dm_info1 = dm_details['dm1_details']
    dm_info2 = dm_details['dm2_details']

    check_dm_details(user1, dm1, dm_info1)
    check_dm_details(user2, dm1, dm_info1)
    check_dm_details(user1, dm2, dm_info2)
    check_dm_details(user2, dm2, dm_info2)
    check_dm_details(user3, dm2, dm_info2)

def test_dm_details_invalid_dmId(users, dms_create):
    '''
    Tests for InputError when DM ID is not a valid DM.
    '''
    user1 = users['user1']
    user2 = users['user2']

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']
    
    invalid_input1 = {
        'token': user1['token'],
        'dm_id': 99
    }

    invalid_input2 = {
        'token': user2['token'],
        'dm_id': -99
    }
    
    assert requests.get(config.url + 'dm/details/v1', params=invalid_input1).status_code == INPUT_ERROR
    assert requests.get(config.url + 'dm/details/v1', params=invalid_input2).status_code == INPUT_ERROR

def test_dm_details_user_not_member(users, spare_users, dms_create):
    '''
    Tests for AccessError when authorised user is 
    not a member of this DM with dm_id.
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, user4 = spare_users

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    # User3 is not a part of dm1.
    invalid_input1 = {
        'token': user3['token'],
        'dm_id': dm1['dm_id']
    }

    # User4 is not a part of dm2.
    invalid_input2 = {
        'token': user4['token'],
        'dm_id': dm2['dm_id']
    }

    assert requests.get(config.url + 'dm/details/v1', params=invalid_input1).status_code == ACCESS_ERROR
    assert requests.get(config.url + 'dm/details/v1', params=invalid_input2).status_code == ACCESS_ERROR

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Dm List ----------------------------------------- #
# --------------------------------------------------------------------------------------- #
def check_dm_list(user, dm_list):
    assert requests.get(config.url + 'dm/list/v1', \
        params={'token': user['token']}).json() == dm_list

def test_dm_list(users, spare_users, list_dms):
    '''
    Tests the intended behaviour of dm list which should
    return a list of DMs that the user is a member of.
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, user4 = spare_users

    dm_list1, dm_list2, dm_list3, dm_list4 = list_dms

    check_dm_list(user1, dm_list1)
    check_dm_list(user2, dm_list2)
    check_dm_list(user3, dm_list3)
    check_dm_list(user4, dm_list4)

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Dm Invite --------------------------------------- #
# --------------------------------------------------------------------------------------- #

def test_valid_dm_invite(users, spare_users, dms_create, dm_details):
    '''
    Tests the intended behaviour of dm invite.
    '''
    user1 = users['user1']
    user2 = users['user2']
    user3, user4 = spare_users

    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    new_dm1 = dm_details['dm1_invite']
    new_dm2 = dm_details['dm2_invite']

    # user1 invite user3 to the dm1
    requests.post(config.url + DM_INVITE, json = 
    {'token': user1['token'],
    'dm_id': dm1['dm_id'], 
    'u_id': user3['auth_user_id']}).json()

    # user2 invite user4 to the dm2
    requests.post(config.url + DM_INVITE, json = 
    {'token': user2['token'],
    'dm_id': dm2['dm_id'], 
    'u_id': user4['auth_user_id']}).json()

    check_dm_details(user3, dm1, new_dm1)
    check_dm_details(user4, dm2, new_dm2)

def test_nonExisting_dm(invalid_input):
    '''
    Tests for InputError when dm_id does not refer to an existing dm.
    '''
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input1']).status_code == INPUT_ERROR
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input2']).status_code == INPUT_ERROR
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input3']).status_code == INPUT_ERROR

def test_nonValid_user(invalid_input):
    '''
    Tests for InputError when u_id does not refer to a valid user.
    '''
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input4']).status_code == INPUT_ERROR
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input5']).status_code == INPUT_ERROR
    assert requests.post(config.url + DM_INVITE, json=invalid_input['invalid_input6']).status_code == INPUT_ERROR

def test_notMember(dms_create):
    '''
    Tests for AccessError when the authorised user is not already a member of the DM.
    '''
    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']

    #Register new users
    new_user1 = requests.post(config.url + REGISTER, json=\
    {
        'email' : 'newuser@email.com',
        'password' : 'userpassword123',
        'name_first' : 'newUser_first',
        'name_last' : 'newUser_last'
    }).json()

    new_user2 = requests.post(config.url + REGISTER, json=\
    {
        'email' : 'newuser1@email.com',
        'password' : 'userpassword1234',
        'name_first' : 'newUserone_first',
        'name_last' : 'newUsertwo_last'
    }).json()
    #The unregistered new_user invites another unregistered new user
    assert requests.post(config.url + DM_INVITE, json=\
    {
        'token': new_user1['token'],
        'dm_id': dm1['dm_id'],
        'u_id': new_user2['auth_user_id']
    }).status_code == ACCESS_ERROR

    #The unregistered new_user invite another registered new_user
    assert requests.post(config.url + DM_INVITE, json=\
    {
        'token': new_user2['token'],
        'dm_id': dm2['dm_id'],
        'u_id': new_user1['auth_user_id']
    }).status_code == ACCESS_ERROR

def test_dm_messages(users, dms_create):
    user = users['user2']
    dm = dms_create['dm1']
    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token' : user['token'],
        'dm_id' : dm['dm_id'],
        'start' : 0
    }).json()
    expected = {
        'messages' : [],
        'start' : 0,
        'end' : -1
    }
    assert resp == expected

def test_dm_messages_invalid_dm(users):
    user1 = users['user1']
    assert requests.get(config.url + 'dm/messages/v1', params={
        'token' : user1['token'],
        'dm_id' : '42',
        'start' : 0
    }).status_code == INPUT_ERROR

def test_dm_messages_invalid_no_access(users,dms_create):
    user3 = users['user3']
    dm = dms_create['dm1']
    assert requests.get(config.url + 'dm/messages/v1', params={
        'token' : user3['token'],
        'dm_id' : dm['dm_id'],
        'start' : 0
    }).status_code == ACCESS_ERROR
# --------------------------------------------------------------------------------------- #
# -------------------------------- Tests for dm_leave ----------------------------------- #
# --------------------------------------------------------------------------------------- #

def test_dm_leave(users, dms_create):
    # Register users
    user1 = users['user1']
    user2 = users['user2']
    user1_profile = requests.get(config.url + 'user/profile/v2', params = {
        'token': user1['token'],
        'u_id': user1['auth_user_id']
    })

    # Create Dm 
    dm1 = dms_create['dm1']
    
    # Leave Dm
    requests.post(config.url + 'dm/leave/v1', json = {
        'token': user2['token'],
        'dm_id': dm1['dm_id']
    })

    assert requests.get(config.url + 'dm/details/v1', params = {
        'token': user1['token'],
        'dm_id':dm1['dm_id']
    }).json()['members'] == [
        {
            'u_id': user1['auth_user_id'], 
            'email': user1_profile['email'],
            'name_first': user1_profile['name_first'],
            'name_last': user1_profile['name_last'],
            'handle_str': user1_profile['handle_str']
        }
    ]

def test_dm_leave_invalid_dm(users, dms_create):
    # Register users
    user1 = users['user1']
    user2 = users['user2']

    # Create Dm
    dm1 = dms_create['dm1']

    assert requests.post(config.url + 'dm/leave/v1', json = {
        'token': user1['token'],
        'dm_id': -1
    }).status_code == InputError

def test_dm_leave_permission(users, dms_create, spare_users):
    # Register users
    user1 = users['user1']
    user2 = users['user2']
    user3, _ = spare_users

    # Create Dm
    dm1 = dms_create['dm1']

    assert requests.post(config.url + 'dm/leave/v1', json = {
        'token': user3['token'],
        'dm_id': dm1['dm_id']
    }).status_code == AccessError

# --------------------------------------------------------------------------------------- #
# -------------------------------- Tests for dm_remove ---------------------------------- #
# --------------------------------------------------------------------------------------- #

def test_dm_remove(users, dms_create):
    # Register users
    user1 = users['user1']
    user2 = users['user2']

    # Create Dm
    dm1 = dms_create['dm1']

    # Remove Dm
    requests.delete(config.url + 'dm/remove/v1', json = {
        'token': user1['token'],
        'dm_id': dm['dm_id']
    })

    assert requests.get(config.url + 'dm/list/v1', params = {
        'token': user1['token']
    }).json()['dms'] == []

def test_dm_remove_invalid_dm(users, dms_create):
    # Register users
    user1 = users['user1']
    user2 = users['user2']

    # Create Dm
    dm1 = dms_create['dm1']

    assert requests.delete(config.url + 'dm/remove/v1', json = {
        'token': user1['token'],
        'dm_id': -1
    }).status_code == InputError
    

def test_dm_remove_permission(users, dms_create):
    # Register users
    user1 = users['user1']
    user2 = users['user2']

    # Create Dm
    dm1 = dms_create['dm1']

    assert requests.delete(config.url + 'dm/remove/v1', json = {
        'token': user2['token'],
        'dm_id': dm1['dm_id']
    }).status_code == AccessError
