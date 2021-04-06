from src.auth import get_data
from src.error import InputError, AccessError
from src.auth import get_data, write_data, check_token, check_u_id
from src.channel import check_channel_id
import jwt
def get_channel_index(channel_id):
    """
    Index the list of channels in data and return the index of the given channel

    Arguments:
        channel_id (int): ID of channel being searched for

    Exceptions:
        None

    Returns:
        Returns i (int) which is the index of the given channel
    """
    data = get_data()
    i = 0
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            return i
        i += 1

def channel_messages_v2(token, channel_id, start):
    '''
    Index the list of channels in data and return the messages from the start index to 
    the end as well as a new end

    Arguments:
        token (str) - session specific user ID
        channel_id (int) - ID of channel of which messages are requested

    Exceptions:
        InputError  - Occurs when channel ID is not a valid ID
        AccessError - Occurs when token is not valid or when user is not a 
            member of the specified channel

    Returns:
        Returns (dict) which contains the messages, the starting index and the end index
    '''
    
    user_index = check_token(token)

    data = get_data()

    # check user is not a removed user
    try:
        check_u_id(data['users'][user_index]['u_id'])
    except InputError:
        raise AccessError(description='User ID is not valid')

    channel_index = check_channel_id(channel_id)

    check_is_member(data['users'][user_index]['u_id'], data['channels'][channel_index]['all_members'])
    
    num_messages= len(data['channels'][channel_index]['messages'])
    if start > num_messages:
        raise InputError('Start is greater than the total number of messages in the channel')
    
    end = start + 50 
    if end > num_messages:
        end = -1
    
    channel_messages = []
    
    if end == -1:
        for message in data['channels'][channel_index]['messages'][-start - 1::-1]:
            channel_messages.append(message)
    else:
        for message in data['channels'][channel_index]['messages'][-start - 1:-end - 1:-1]:
            channel_messages.append(message)
    
    return {'messages' : channel_messages, 'start' : start, 'end' : end}

# Creates a new channel with that name that is either a public or private channel
def channels_create_v2(token, name, is_public, is_dm=False):
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