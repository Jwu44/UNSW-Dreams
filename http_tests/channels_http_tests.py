'''
Authors: William Zheng, z5313015
Date: 21/03/2021
'''
import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

ACCESS_ERROR = 403
INPUT_ERROR = 400

def register_users():
    return {
        'user1':{
            'email': 'authuser@gmail.com',
            'password': 'password321',
            'name_first': 'Auth' ,
            'name_last': 'User',
        },
        'user2':{
            'email': 'firstlast@gmail.com',
            'password': 'password321',
            'name_first': 'First' ,
            'name_last': 'Last',
        }
    }

@pytest.fixture
def users():
    return users_function()

# Return 2 registered users.
def users_function():
    requests.delete(config.url + 'clear/v1')
    user1 = requests.post(config.url + 'auth/register/v2', json = register_users()['user1']).json()
    user2 = requests.post(config.url + 'auth/register/v2', json = register_users()['user2']).json()
    return {
        'user1': user1,
        'user2': user2
    }

@pytest.fixture
def channels_create(users):
    public = requests.post(config.url + 'channels/create/v2', json = {
        'token': users['user1']['token'],
        'name': 'Public Channel',
        'is_public': True
    }).json()
    private = requests.post(config.url + 'channels/create/v2', json = {
        'token': users['user1']['token'],
        'name': 'Private Channel',
        'is_public': False
    }).json()

    return (public, private)

#Channel list to be returned.
def list_channels(channel1, channel2):
    return {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'channel_name': 'Public Channel'
            },
            {
                'channel_id': channel2['channel_id'],
                'channel_name': 'Private Channel'
            },
        ]
    }


def test_channels_create_inputerror(users):
    invalid_param1 = {
        'token': users['user1']['token'], 
        'name': 'Pub'*20,
        'is_public': True 
    }
    invalid_param2 = {
        'token': users['user1']['token'], 
        'name': 'x'*21,
        'is_public': False
    }
    assert requests.post(config.url + 'channels/create/v2', json = invalid_param1).status_code == INPUT_ERROR
    assert requests.post(config.url + 'channels/create/v2', json = invalid_param2).status_code == INPUT_ERROR

