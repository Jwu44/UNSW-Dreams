'''
Authors: Justin Wu, z5316037

Date: 31 March 2021
'''
import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from http_tests.helpers_http_test import create_channel, register_user, send_message, get_channel_messages
from http_tests.channels_http_test import register_users, users, channels_create

ACCESS_ERROR = 403
INPUT_ERROR = 400

# --------------------------------------------------------------------------------------- #
# ----------------------------- Fixture for Dm_Create  ---------------------------------- #
# --------------------------------------------------------------------------------------- #
@pytest.fixture
def dms_create(users):
    '''
    Setting up 2 dms:
        - Dm from User1 to User2
        - Dm from User2 to User1 & User3 
    '''
    user1 = users['user1']
    user2 = users['user2']

    # Creating User3
    user3 = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'MarcChee@gmail.com',
        'password': 'asldfkj34kj',
        'name_first': 'Marc' ,
        'name_last': 'Chee',
    }).json()

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
        'user3': user3
    }
# --------------------------------------------------------------------------------------- #
# ----------------------------- Helper Function  ---------------------------------------- #
# --------------------------------------------------------------------------------------- #
def channel_messages_input(user, channel, start):
    '''
    Returns a list of recent messages.
    '''
    messages = requests.get(config.url + 'channel/messages/v2', \
        params={'token': user['token'], 'channel_id': channel['channel_id'], 'start': start}).json()
    return messages

def dm_messages_input(user, dm, start):
    '''
    Returns a list of recent messages.
    '''
    messages = requests.get(config.url + 'dm/messages/v1', \
        params={'token': user['token'], 'dm_id': dm['dm_id'], 'start': start}).json()
    return messages
# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Message Send ------------------------------------ #
# --------------------------------------------------------------------------------------- #
def test_message_send(users, channels_create):
    '''
    Tests the intended behavior of message send when
    a user sends a message to a channel they've created. 
    '''
    user1 = users['user1']
    channel, _ = channels_create

    # User1 sends a message to the channel
    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Testing'
    }).json()['message_id']

    msg_list = channel_messages_input(user1, channel, 0)['messages'][0]

    assert message_id == msg_list['message_id']
    assert msg_list['message'] == 'Testing'
    assert msg_list['u_id'] == user1['auth_user_id']

def test_message_send_InputError(users, channels_create):
    '''
    Test message_send for InputError when message
    contains over 1000 characters. 
    '''
    user1 = users['user1']
    channel, _ = channels_create

    invalid_message = {
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'x'*1001
    }
    assert requests.post(config.url + 'message/send/v2', json=invalid_message).status_code == INPUT_ERROR

def test_message_send_AccessError(users, channels_create):
    '''
    Test message_send for AccessError when 
    the authorised user has not joined the channel 
    they are trying to post to.
    '''
    # User2 is the user who hasn't joined user1's channel
    user2 = users['user2']
    channel, _ = channels_create

    invalid_message = {
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello'
    }
    assert requests.post(config.url + 'message/send/v2', json=invalid_message).status_code == ACCESS_ERROR

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Message Edit ------------------------------------ #
# --------------------------------------------------------------------------------------- #
def test_message_edit(users, channels_create):
    '''
    Tests the intended behavior of message edit when
    a user edits a message they've sent to the channel
    they've created. 
    '''
    owner = users['user1']
    channel, _ = channels_create

    # Owner sends a message to the channel
    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'Helo Word'
    }).json()['message_id']

    # Owner edits their message
    requests.put(config.url + 'message/edit/v2', json = {
        'token': owner['token'],
        'message_id': message_id,
        'message': 'Hello World!'
    })

    msg_list = channel_messages_input(owner, channel, 0)['messages'][0]
    assert msg_list['message_id'] == message_id
    assert msg_list['message'] == 'Hello World!'
    assert msg_list['u_id'] == owner['auth_user_id']

def test_message_empty(users, channels_create):
    '''
    Tests the intended behavior of message edit when
    a user wants to edit a message with an empty string.
    '''
    owner = users['user1']
    channel, _ = channels_create

    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'Helo Word'
    }).json()['message_id']

    # Empty string should remove old message
    requests.put(config.url + 'message/edit/v2', json = {
        'token': owner['token'],
        'message_id': '',
        'message': 'Hello World!'
    })

    msg_list = channel_messages_input(owner, channel, 0)['messages'][0]
    assert msg_list['message_id'] == message_id
    assert msg_list['message'] == ''
    assert msg_list['u_id'] == owner['auth_user_id']

def test_message_edit_too_long(users, channels_create):
    '''
    Test message_edit for InputError when message
    contains over 1000 characters. 
    '''
    owner = users['user1']
    channel, _ = channels_create

    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hey'
    }).json()['message_id']

    invalid_message = {
        'token': owner['token'],
        'message_id': message_id,
        'message': 'a'*1001
    }
    assert requests.put(config.url + 'message/edit/v2', json=invalid_message).status_code == INPUT_ERROR

def test_edit_removed_message(users, channels_create):
    '''
    Test message_edit for InputError when message_id 
    refers to a deleted message.
    '''
    owner = users['user1']
    channel, _ = channels_create

    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hey'
    }).json()['message_id']

    # Message is removed from the channel
    requests.delete(config.url + 'message/remove/v1', json={
        'token': owner['token'],
        'message_id': message_id
    })

    assert requests.put(config.url + 'message/edit/v2', json={
        'token': owner['token'],
        'message_id': message_id,
        'message': 'Hello World!'
    }).status_code == INPUT_ERROR


def test_message_edit_not_auth_user(users, channels_create):
    '''
    Test message_edit for AccessError when message 
    with message_id was not sent by the authorised user 
    making the request.
    '''
    owner = users['user1']
    user2 = users['user2']
    channel, _ = channels_create

    # Owner sends a message
    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hey'
    }).json()['message_id']

    # User2 attempts to edit owner's message
    assert requests.put(config.url + 'message/edit/v2', json={
        'token': user2['token'],
        'message_id': message_id,
        'message': 'Hello World!'
    }).status_code == ACCESS_ERROR


def test_message_edit_not_channel_owner(users, channels_create):
    '''
    Test message_edit for AccessError when the authorised user 
    is not an owner of this channel (if it was sent to a channel) 
    or the **Dreams**.
    '''
    owner = users['user1']
    user2 = users['user2']
    channel, _ = channels_create

    # Owner invites user2 to channel.
    requests.post(config.url + 'channel/invite/v2', json = {
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['auth_user_id']
    })

    # User2 sends a message to the channel.
    message_id = requests.post(config.url + 'message/send/v2', json = {
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hi'
    }).json()['message_id']

    # User2 shouldn't be able to edit message.
    assert requests.put(config.url + 'message/edit/v2', json={
        'token': user2['token'],
        'message_id': message_id,
        'message': 'Hi !!!'
    }).status_code == ACCESS_ERROR

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Message SendDm ---------------------------------- #
# --------------------------------------------------------------------------------------- #
def test_message_senddm(users, dms_create, channels_create):
    '''
    Tests the intended behavior of message senddm when
    a user sends a message to a channel they've created. 
    '''
    user1 = users['user1']
    user3 = dms_create['user3']
    
    dm1 = dms_create['dm1']
    dm2 = dms_create['dm2']
    
    channel1, _ = channels_create

    # User1 sends a message to dm1
    message_id1 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': user1['token'],
        'dm_id': dm1['dm_id'],
        'message': 'COMP1531'
    }).json()['message_id']

    msg_list1 = channel_messages_input(user1, dm1, 0)['messages'][0]

    assert message_id1 == msg_list1['message_id']
    assert msg_list['message'] == 'COMP1531'
    assert msg_list['u_id'] == user1['auth_user_id']

    # User3 sends a message to dm2
    message_id2 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': user3['token'],
        'dm_id': dm2['dm_id'],
        'message': 'Testing'
    }).json()['message_id']

    msg_list2 = channel_messages_input(user3, dm2, 0)['messages'][0]

    assert message_id2 == msg_list2['message_id']
    assert msg_list['message'] == 'Testing'
    assert msg_list['u_id'] == user3['auth_user_id']

    # User1 sends same message sent to dm1 but to channel1
    message_id3 = requests.post(config.url + 'message/send/v2', json = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'COMP1531'
    }).json()['message_id']

    msg_list3 = channel_messages_input(user1, channel, 0)['messages'][0]

    assert message_id3 == msg_list3['message_id']
    assert msg_list['message'] == 'COMP1531'
    assert msg_list['u_id'] == user1['auth_user_id']

def test_message_senddm_too_long(users, dms_create):
    '''
    Test message_senddm for InputError when message
    contains over 1000 characters. 
    '''
    user1 = users['user1']
    user2 = users['user1']
    user3 = dms_create['user3']

    dm1 = dms_create['dm1']['dm_id']
    dm2 = dms_create['dm2']['dm_id']

    invalid_message1 = {
        'token': user1['token'],
        'dm_id': dm1,
        'message': 'a'*1001
    }
    invalid_message2 = {
        'token': user2['token'],
        'dm_id': dm2,
        'message': 'b'*1001
    }
    invalid_message3 = {
        'token': user3['token'],
        'dm_id': dm2,
        'message': 'c'*1001
    }

    assert requests.post(config.url + 'message/senddm/v1', json=invalid_message1).status_code == INPUT_ERROR
    assert requests.post(config.url + 'message/senddm/v1', json=invalid_message2).status_code == INPUT_ERROR
    assert requests.post(config.url + 'message/senddm/v1', json=invalid_message3).status_code == INPUT_ERROR

def test_message_senddm_auth_not_member(users, dms_create):
    '''
    Test message_senddm for AccessError when auth user
    is not a member of the DM they are trying to post to.
    '''
    # User3 is not a part of dm1.
    user3 = dms_create['user3']
    dm1 = dms_create['dm1']['dm_id']

    invalid_message = {
        'token': user3['token'],
        'dm_id': dm1,
        'message': 'Hi'
    }

    assert requests.post(config.url + 'message/senddm/v1', json=invalid_message).status_code == ACCESS_ERROR

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Message Remove ---------------------------------- #
# --------------------------------------------------------------------------------------- #

def test_message_remove_public(users, channels_create):
    '''
    Tests the intended behavior of message remove for a public channel.
    '''
    # Register User
    auth = users['user1']
    # Create Channel
    channel, _ = channels_create
    # Send messages
    message1 = send_message(auth['token'], channel['channel_id'], 'Test Message 1')
    message2 = send_message(auth['token'], channel['channel_id'], 'Test Message 2')
    # Remove message
    requests.delete(config.url + 'message/remove/v1', json = {
        'token': auth['token'],
        'message_id': message1['message_id']
    })
    # Get messages   
    all_messages = get_channel_messages(auth['token'], channel['channel_id'], 0)
    assert all_messages['messages'][0]['message_id'] == message1['message_id']

def test_message_remove_private(users, channels_create):
    '''
    Tests the intended behavior of message remove for a private channel.
    '''
    # Register User
    auth = users['user1']
    # Create Channel
    _, channel = channels_create
    # Send messages
    message1 = send_message(auth['token'], channel['channel_id'], 'Test Message 1')
    message2 = send_message(auth['token'], channel['channel_id'], 'Test Message 2')
    # Remove message
    requests.delete(config.url + 'message/remove/v1', json = {
        'token': auth['token'],
        'message_id': message1['message_id']
    })
    # Get messages   
    all_messages = get_channel_messages(auth['token'], channel['channel_id'], 0)
    assert all_messages['messages'][0]['message_id'] == message1['message_id'] 


def test_message_remove_dm(users, dms_create):
    '''
    Tests the intended behavior of message remove for a dm.
    '''
    # Register User
    auth = users['user1']
    user = users['user2']
    # Create DM
    dm = dms_create['dm1']
    # Send message
    message1 = send_message(auth['token'], dm['dm_id'], 'Test Message 1')
    message2 = send_message(auth['token'], dm['dm_id'], 'Test Message 2')    
    # Remove message
    requests.delete(config.url + 'message/remove/v1', json = {
        'token': auth['token'],
        'message_id': message1['message_id']
    })
    # Get messages    
    all_messages = get_channel_messages(auth['token'], dm['dm_id'], 0)
    assert all_messages['messages'][0]['message_id'] == message1['message_id']

# --------------------------------------------------------------------------------------- #
# ----------------------------- Testing Message Share ----------------------------------- #
# --------------------------------------------------------------------------------------- #
def test_message_share(users, channels_create, dms_create):
    '''
    Tests the intended behavior of message share.
    '''
    user1 = users['user1']
    user2 = users['user2']
    public, private = channels_create
    dm1 = dms_create['dm1']

    # User1 sends a message to the channel
    message_sent = requests.post(config.url + 'message/send/v2', json = {
        'token': user1['token'],
        'channel_id': public['channel_id'],
        'message': 'Testing'
    }).json()['message_id']

    # User1 shares message to priv channel and dm
    message_shared_priv = requests.post(config.url + 'message/share/v1', json = {
        'token': user1['token'],
        'og_message_id': message_sent,
        'message': '123',
        'channel_id': private['channel_id'],
        'dm_id': -1
    }).json()['shared_message_id']

    message_shared_dm = requests.post(config.url + 'message/share/v1', json = {
        'token': user1['token'],
        'og_message_id': message_sent,
        'message': 'abc',
        'channel_id': dm1['dm_id'],
        'dm_id': -1
    }).json()['shared_message_id']

    msg_priv_list = channel_messages_input(user1, private, 0)['messages'][0]
    assert message_shared_priv == msg_priv_list['message_id']
    assert msg_priv_list['message'] == 'Testing, 123'
    assert msg_priv_list['u_id'] == user1['auth_user_id']

    msg_dm_list = dm_messages_input(user2, dm1, 0)['messages'][0]
    assert message_shared_dm == msg_dm_list['message_id']
    assert msg_dm_list['message'] == 'Testing, abc'
    assert msg_dm_list['u_id'] == user1['auth_user_id']

def test_message_share_access_error(users, channels_create, dms_create):
    '''
    Tests for AccessError when the authorised user has not joined the channel or DM they are trying to share the message to. 
    '''
    user1 = users['user1']
    public, private = channels_create
    dm1 = dms_create['dm1']

    new_user = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'haydensmith@gmail.com',
        'password': 'pwrd321',
        'name_first': 'Hayden' ,
        'name_last': 'Smith',
    }).json()

    # User1 sends a message to the channel
    message_sent = requests.post(config.url + 'message/send/v2', json = {
        'token': user1['token'],
        'channel_id': public['channel_id'],
        'message': 'Testing'
    }).json()['message_id']

    # New User tries to share message
    assert requests.post(config.url + 'message/share/v1', json = {
        'token': new_user['token'],
        'og_message_id': message_sent,
        'message': 'abc',
        'channel_id': private,
        'dm_id': -1
    }).status_code == ACCESS_ERROR

    assert requests.post(config.url + 'message/share/v1', json = {
        'token': new_user['token'],
        'og_message_id': message_sent,
        'message': 'abc',
        'channel_id': dm1['dm_id'],
        'dm_id': -1
    }).status_code == ACCESS_ERROR
