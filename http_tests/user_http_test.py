'''
Authors:
    Alec Dudley-Bestow, z5260201

Date:
    26 March 2021
'''
import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from http_tests.auth_http_test import REGISTER

ACCESS_ERROR = 403
INPUT_ERROR = 400

#used to register new users easily
def register_input():
    return {
        'user1' : {'email' : 'validemail@email.com',
            'password' : 'validpassword',
            'name_first' : 'thisisalongfirstname',
            'name_last' : 'lastname'
        },
        'user2' : {'email' : 'anothervalidemail@email.com',
            'password' : 'adifferentvalidpassword',
            'name_first' : 'thisisalongfirstname',
            'name_last' : 'lastname'
        },
        'user3' : {'email' : 'email@email.com',
            'password' : 'asdf',
            'name_first' : 'asdfasdfsdfdsf',
            'name_last' : 'lastname'
        },
    }

@pytest.fixture
def users():
    return users_function()

#register new users to help in testing
def users_function():
    requests.delete(config.url + 'clear/v1')
    user1 = requests.post(config.url + REGISTER, json = register_input()['user1']).json()
    user2 = requests.post(config.url + REGISTER, json = register_input()['user2']).json()
    user3 = requests.post(config.url + REGISTER, json = register_input()['user3']).json()
    return {'user1' : user1, 'user2' : user2, 'user3' : user3}

#the profiles to be return of the registered users according to the spec
@pytest.fixture
def profiles(users):
    registered = register_input()
    profile1 = {'email' : registered['user1']['email'],
        'u_id' : users['user1']['auth_user_id'],
        'name_first' : registered['user1']['name_first'],
        'name_last' : registered['user1']['name_last'],
        'handle_str' : 'thisisalongfirstname'
    }
    
    profile2 = {'email' : registered['user2']['email'],
        'u_id' : users['user2']['auth_user_id'],
        'name_first' : registered['user2']['name_first'],
        'name_last' : registered['user2']['name_last'],
        'handle_str' : 'thisisalongfirstname0'
    }
    return {'profile1' : profile1, 'profile2' : profile2}  

@pytest.fixture
def invalid_user():
    return invalid_user_function()

#returns a user with an invalid token and a user with a valid token
def invalid_user_function():
    invalid_user = users_function()['user2']
    requests.delete(config.url + 'clear/v1')
    return {'invalid' : invalid_user, \
        'valid' : requests.post(config.url + REGISTER, json = register_input()['user2']).json()}    

#helper function that asserts that a given url throws an access error when given valid data
def put_access_error(url, data):
    data['token'] = invalid_user_function()['invalid']['token']
    assert requests.put(config.url + url, json=data).status_code == ACCESS_ERROR

#helper function that asserts that a given url throws an input error when given invalid data
def put_input_error(url, invalid_data):
    invalid_data['token'] = invalid_user_function()['valid']['token']
    assert requests.put(config.url + url, json=invalid_data).status_code == INPUT_ERROR

def check_profile(user, profile):
    assert requests.get(config.url + 'user/profile/v2', \
        params={'token':user['token'], 'u_id' : user['auth_user_id']}).json() == profile

#test for all functions, checking they throw an access error when given an invalid token:
def test_user_profile_accesserror(invalid_user):
    param = {'token':invalid_user['invalid']['token'], 'u_id':invalid_user['valid']['auth_user_id']}
    assert requests.get(config.url + 'user/profile/v2', params=param).status_code == ACCESS_ERROR

def test_users_all_accesserror(invalid_user):
    assert requests.get(config.url + 'users/all/v1', \
        params={'token' : invalid_user['invalid']['token']}).status_code == ACCESS_ERROR

def test_user_setname_accesserror(invalid_user):
    put_access_error('user/profile/setname/v2', \
        {'name_first':'newfirstname', 'name_last':'newlastname'})

def test_user_setemail_accesserror(invalid_user):
    put_access_error('user/profile/setemail/v2', {'email':'new@email.com'})

def test_user_sethandle_accesserror(invalid_user):
    put_access_error('user/profile/sethandle/v1', {'handle_str':'validhandle'})


#test for all functions, checking they throw an input error when given incorrect input:
def test_user_profile_inputerror(invalid_user):
    param = {'token':invalid_user['valid']['token'], 'u_id':invalid_user['invalid']['auth_user_id']}
    assert requests.get(config.url + 'user/profile/v2', params=param).status_code == INPUT_ERROR

def test_user_setname_inputerror(invalid_user):
    put_input_error('user/profile/setname/v2', \
        {'name_first':'', 'name_last':'x'*51})

def test_user_setemail_inputerror(invalid_user):
    put_input_error('user/profile/setemail/v2', {'email':'invalidemail@.com'})
    
def test_user_sethandle_inputerror(invalid_user):
    put_input_error('user/profile/sethandle/v1', {'handle_str':'invalidhandle'*21})
    

#tests for all functions, checking they output according to specifications
def test_user_profile(users, profiles):
    check_profile(users['user1'], profiles['profile1'])

def test_users_all(users, profiles):
    user_list = requests.get(config.url + 'users/all/v1', \
        params={'token':users['user1']['token']}).json()['users']
    assert profiles['profile1'] in user_list
    assert profiles['profile2'] in user_list
    
def test_user_setname(users, profiles):
    requests.put(config.url + 'user/profile/setname/v2', \
        json={'token':users['user1']['token'], \
        'name_first':'newfirstname', 'name_last':'newlastname'})
        
    profiles['profile1']['name_first'] = "newfirstname"
    profiles['profile1']['name_last'] = 'newlastname'
    check_profile(users['user1'], profiles['profile1'])

def test_user_setemail(users, profiles):
    requests.put(config.url + 'user/profile/setemail/v2', \
        json={'token':users['user1']['token'], 'email':'new@email.com'})
    profiles['profile1']['email'] = "new@email.com"
    check_profile(users['user1'], profiles['profile1'])
    
def test_user_sethandle(users, profiles):
    requests.put(config.url + 'user/profile/sethandle/v1', \
        json={'token':users['user1']['token'], 'handle_str':'thisisanewhandle'})
    profiles['profile1']['handle_str'] = "thisisanewhandle"
    check_profile(users['user1'], profiles['profile1'])
