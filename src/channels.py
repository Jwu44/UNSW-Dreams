'''
Authors: 
    William Zheng, z5313015
    Justin Wu, z5316037

Date:
    01 March 2021
'''

from src.auth import get_data, write_data, check_token
from src.channel import user_id_valid
from src.error import InputError, AccessError
from src.user import user_profile

import jwt

SECRET = 'atotallysecuresecret'

def channels_list(token, is_dm=False):
    '''
    Given a user ID, if the ID is valid, this function returns a list of channels 
    the user is a part of (and their associated details).

    Arguments:
        auth_user_id (int): ID of current user.

    Exceptions:
        AccessError - Occurs when user  ID is not authorised or when user is not a 
        member of the specified channel

    Returns:
        Returns channel_dict(dictionary) which contains a list of dictionaries.
   
    '''
    # Check if auth_user exists in the database
    data = get_data()
    
    user = check_token(token)

    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = token_structure['u_id']
    
    if is_dm:
        dm_dict = {
            'dms': []
        }
        
        dm_list = dm_dict['dms']

        for channel in data['channels']:
            if is_dm == channel['is_dm']:
                dm = {
                    'dm_id': channel['channel_id'],
                    'dm_name': channel['channel_name']
                }
                for member in channel['all_members']:
                    if member['u_id'] == u_id:
                        dm_list.append(dm)
        return dm_dict

    if not is_dm: 
        channel_dict = {
            'channels': []
        }

        channel_list = channel_dict['channels']

        # Loop through all channels stored in data file.
        for channel in data['channels']:
            if is_dm == channel['is_dm']:
                # Get details of the current channel.
                curr_channel = {
                    'channel_id': channel['channel_id'],
                    'channel_name': channel['channel_name']
                }
                for member in channel['all_members']:
                    if member["u_id"] == u_id:
                        channel_list.append(curr_channel)
        return channel_dict
    

def channels_listall(token, is_dm=False):
    '''
    Given a user ID, if the ID is valid, this function returns
    a list of all channels in the database (and their associated details).

    Arguments:
        auth_user_id (int): ID of current user.

    Exceptions:
        AccessError - Occurs when user  ID is not authorised or when user is not a 
        member of the specified channel

    Returns:
        Returns channel_dict(dictionary) which contains a list of dictionaries.
   
    '''
    data = get_data()
    
    check_token(token)

    channel_dict = {
        'channels': []
    }

    channel_list = channel_dict['channels']
    
    # Loop through all channels stored in data file.
    for channel in data['channels']:
        if is_dm == channel['is_dm']: 
            # Get channel details and append it to the list
            curr_channel = {
                'channel_id': channel['channel_id'],
                'channel_name': channel['channel_name']
            }
            channel_list.append(curr_channel)

    return channel_dict


# Creates a new channel with that name that is either a public or private channel
def channels_create(token, name, is_public, is_dm=False):
    """
    Creates a new channel with that name that is either a public or private channel.

    Arguments:
        token(string): Id of user in a certain session.
        name (string): Name of the channel.
        is_public (bool): Whether the channel is public or private.

    Exceptions:
        InputError - Invalid auth_user_id.
        InputError - Channel name is longer than 20 chars or is 0 chars.

    Return Value:
        Dictionary with item "channel_id".
    """
    data = get_data()

    # Validate token
    check_token(token)

    # Name is longer than 20 chars long.
    if not is_dm and len(name) > 20:
        raise InputError(description="Channel name is longer than 20 characters")

    # Name is empty.
    if len(name) == 0:
        raise InputError(description="Invalid channel name!")

    # Decode token to get the u_id
    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = token_structure['u_id']

    # Look into the database to find a new channel_id.
    channel_id = channel_id_generate(data['channels'])

    # Decode token to get the u_id
    token_structure = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = token_structure['u_id']

    # Add channel details to the database.
    channel_details = create_channel_details(channel_id, name, token, u_id, is_public, is_dm)
    data['channels'].append(channel_details)
    write_data(data)

    return {
        'channel_id': channel_id,
    }


def channel_id_generate(all_channels):
    """
    Generates a channel id for a given channel.

    Arguments:
        all_channels (list): Contains a list of existing channels.

    Return Value:
        Available channel_id (int).
    """
    channel_id = 1
    for channel in all_channels:
        if channel['channel_id'] == channel_id:
            # Keep incrementing channel_id by 1 until we get a new channel_id
            channel_id += 1
    return channel_id

def create_channel_details(channel_id, name, token, u_id, is_public, is_dm):
    """
    Adds channel details to the database.

    Paramters:
        channel_id (int): Id of channel being created.
        name (string): Name of the channel.
        u_id (int): The channel creator's id.
        is_public (bool): Whether the channel is public or private.

    Returns:
        Available channel_id (int)
    """
    owner_details = []
    owner_details.append({'u_id': u_id})

    # The only member that exists is the owner
    all_member_details = []
    all_member_details.append({'u_id': u_id})

    channel_details = {
        'channel_id' : channel_id,
        'channel_name' : name,
        'owner_members' : owner_details,
        'all_members' : all_member_details,
        'is_public' : is_public,
        'is_dm' : is_dm,
        'messages' : []
    }
    return channel_details


