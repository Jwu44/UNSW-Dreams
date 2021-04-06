'''
Authors:
    Justin Wu, z5316037

Date:
    25 March 2021
'''

from src.error import InputError, AccessError
from src.auth import auth_register, check_token, get_data, write_data, check_u_id
from src.channels import channels_create
from src.channel import channel_id_valid, member_check, get_channel_index, user_is_owner_token
from datetime import datetime, timezone
from src.other import insert_tag_notification

import jwt

SECRET = 'atotallysecuresecret'

def message_send(token, channel_id, message):
    '''
        Send a message from authorised_user to the channel specified by channel_id. 
        Note: Each message should have it's own unique ID. 
        I.E. No messages should share an ID with another message, 
        even if that other message is in a different channel.
    Arguments:
        token (string) - JWT token encrypted with user's u_id and session_id.
        channel_id (int) - Id of inputted channel.
        message (string) - User's message to the specified channel.

    Exceptions:
        InputError - Message is more than 1000 characters.
        AccessError - When the authorised user has not joined the channel they are trying to post to.

    Return Value:
        Dictionary containing 'message_id'.
    ''' 
    check_token(token)

    data = get_data()
    if not channel_id_valid(channel_id, data['channels']):
        raise InputError(description="Invalid channel id!")
    
    message_too_long(message)
    
    # Decode token to get u_id
    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = token_structure['u_id']
    if not member_check(u_id, channel_id, data['channels']):
        raise AccessError(description="User is not a member of the channel!")

    # Generate unique id for message
    message_id = message_id_generate()

    # Go to the channel and append the message and message_id
    channel_index = get_channel_index(channel_id)
    utc_time = datetime.utcnow().timestamp()
    time = datetime.fromtimestamp(utc_time).strftime('%Y-%m-%d')
    data['channels'][channel_index]['messages'].append({
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': time
    })
    write_data(data)
    insert_tag_notification(token, channel_id, message)
    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    ''' 
    Given a message_id for a message, this message is removed from the channel/DM
    
    Parameters:
        token 
        message_id 

    Exceptions:
        InputError - 
        AccessError - 
        AccessError - 

    Returns:
        None
    '''
    data = get_data()
    user_index = check_token(token)

    # Message doesnt exist
    message, channel = message_id_exists(message_id)
    if message == None:
        raise InputError

    # Message not sent by authorised user
    if message_is_sender(data['users'][user_index]['u_id'], message) == False:
        raise AccessError

    # Auth user is not owner of channel or dreams
    # NOTE Function is imported from channel so not on this branch
    if user_is_owner_token(token, channel['channel_id']) == False:
        raise AccessError

    for ch in data['channels']:
        if ch['channel_id'] == channel['channel_id']:
            ch['messages'].remove(message)

    write_data(data)
    return {}

def message_edit(token, message_id, message):
    '''
    Given a message, update its text with new text. 
    If the new message is an empty string, the message is deleted.

    Arguments:
        token (string) - JWT token encrypted with user's u_id and session_id.
        message_id (int) - Id of message to be edited.
        message (string) - Autherised user's message to the specified channel.

    Exceptions:
        InputError - Length of new message is over 1000 characters.
        InputError - Message_id refers to a deleted message.
        AccessError - Different user is trying to edit another user's message.
        AccessError - The user trying to edit their message is not an owner of the channel/dm.
    
    Return:
        None
    '''
    data = get_data()

    # InputError - Length of new message is over 1000 characters.
    message_too_long(message)

    check_token(token)
    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = token_structure['u_id']

    # InputError - Message_id refers to a deleted message.
    channel_id, msg_index = search_message_id(message_id)
    channel_index = get_channel_index(channel_id)
    check_u_id(auth_user_id)

    # AccessError - The user trying to edit their message is not an owner of the channel/dm.
    owner_check(data['channels'][channel_index]['owner_members'], auth_user_id)

    # If given empty string
    if len(message) == 0:
        message_remove(token, message_id)
    
    # Otherwise edit the old message.
    data['channels'][channel_index]['messages'][msg_index]['message'] = message

    # AccessError - Different user is trying to edit another user's message.
    u_id = data['channels'][channel_index]['messages'][msg_index]['u_id']
    if auth_user_id != u_id:
        raise AccessError(description="User trying to edit the message is not the auth user who made the message!")
    
    write_data(data)
    return {
    }

def message_senddm(token, dm_id, message):
    '''
    Send a message from authorised_user to the DM specified by dm_id. Note: Each message should 
    have it's own unique ID. I.E. No messages should share an ID with another message, even if 
    that other message is in a different channel or DM.

    Arguments:
        token (string) - JWT token encrypted with user's u_id and session_id.
        dm_id (int) - Id of inputted dm.
        message (string) - User's message to the specified channel.
    
    Exceptions:
        InputError - Length of new message is over 1000 characters.
        AccessError - When the authorised user is not a member of the DM they are trying to post to.
    
    Return Value:
        Dictionary containing 'message_id'.
    '''
    dm_msg_id = message_send(token, dm_id, message)['message_id']

    return {
        'message_id': dm_msg_id
    }

def message_share(token, og_message_id, message, channel_id, dm_id):
    '''
    Given a message_id, auth_user will share this messageto a channel or dm. 
    If an optional message is given, it is added in addition to the originally shared message.

    Arguments:
        token (string) - JWT token encrypted with user's u_id and session_id.
        og_message_id (int) - Id of the original message. 
        message(string) - Message is the optional message in addition to the shared message, and will be an empty string '' if no message is given
        channel_id (int) - Channel Id that the message is being shared to, and is -1 if it is being sent to a DM.
        dm_id (int) - Dm Id that the message is being shared to, and is -1 if it is being sent to a channel.
    
    Exceptions:
        AccessError - When the authorised user has not joined the channel or DM they are trying to share the message to.
    
    Returns:
        Dicitonaring containing a shared_message_id
    '''
    data = get_data()

    check_token(token)

    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = token_structure['u_id']

    # First fetch the actual og message from og_msg_id.
    og_channel_id, og_msg_index = search_message_id(og_message_id)
    og_channel_index = get_channel_index(og_channel_id)

    # Get a copy of the message.
    og_message = data['channels'][og_channel_index]['messages'][og_msg_index]['message']

    # Shared message combines the og_message and an optional message.
    shared_msg = og_message + ", " + message

    # Sending to dm.
    if channel_id == -1:
        if not member_check(u_id, dm_id, data['channels']):
            raise AccessError(description="User is not a member of the channel!")
        shared_message_id = message_senddm(token, dm_id, shared_msg)['message_id']

    # Sending to channel
    if dm_id == -1:
        if not member_check(u_id, channel_id, data['channels']):
            raise AccessError(description="User is not a member of the channel!")
        shared_message_id = message_send(token, channel_id, shared_msg)['message_id']

    return {
        'shared_message_id': shared_message_id,
    }

############################################################
#            Helper functions                              #      
############################################################
# Creates a new unique id for message.
def message_id_generate():
    data = get_data()
    message_id = 1
    # Search across all channels and all messages.
    for channels in data['channels']:
        for message in channels['messages']:
            if message['message_id'] == message_id:
                message_id += 1
    return message_id

def message_too_long(message):
    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters!")

def search_message_id(message_id):
    '''
    Given a message_id, search the channel database to return channel_id & the index of the message.
    '''
    data = get_data()
    for channel in data['channels']:
        for msg_index, message in enumerate(channel['messages']):
            if message['message_id'] == message_id:
                return (channel['channel_id'], msg_index)
    
    # Message not found.
    raise InputError(description="Message_id is not valid!")

def owner_check(owner_members, u_id):
    for member in owner_members:
        if member['u_id'] == u_id:
            return True
    raise AccessError(description="Authorised user is NOT an owneer of this channel!")
    
def message_id_exists(message_id):
    data = get_data()
    for channel in data['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return (message, channel)
    return (None, None)

def message_is_sender(u_id, message):
    if u_id == message['u_id']:
        return True
    return False

