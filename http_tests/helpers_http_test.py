import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

def register_user(email, password, name_first, name_last):
    resp = requests.post(config.url + 'auth/register', json = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    })
    return resp.json()

def create_channel(token, is_public, channel_name):
    resp = requests.post(config.url + 'channels/create/v2', json = {
        'token': token,
        'name': channel_name,
        'is_public': is_public
    })
    return resp.json()

def send_message(token, channel_id, message):
    resp = requests.post(config.url + 'message/send/v2', json = {
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    return resp.json()

def get_channel_messages(token, channel_id, start):
    resp = requests.get(config.url + 'channel/messages/v2', params = {
        'token': token,
        'channel_id': channel_id,
        'start': start
    })
    return resp.json()