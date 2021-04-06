import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import other, config, channel, channels, auth, user, dm, message

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route('/channels/create/v2', methods=['POST'])
def channels_create():
    return dumps(channels.channels_create(**request.get_json()))

@APP.route('/channel/invite/v2', methods=['POST'])
def channel_invite():
    return dumps(channel.channel_invite(**request.get_json()))

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details():
    return dumps(channel.channel_details(request.args.get('token'), int(request.args.get('channel_id'))))

@APP.route('/channel/join/v2', methods=['POST'])
def channel_join():
    return dumps(channel.channel_join(**request.args.get_json()))

@APP.route('/channel/messages/v2', methods=['GET'])
def channel_messages():
    return dumps(channel.channel_messages(request.args.get('token'), int(request.args.get('channel_id')), int(request.args.get('start'))))

@APP.route('/channels/list/v2', methods=['GET']) 
def channels_list(): 
    return dumps(channels.channels_list(request.args.get('token'))) 

@APP.route('/channels/listall/v2', methods=['GET']) 
def channels_listall(): 
    return dumps(channels.channels_listall(request.args.get('token'))) 
    
@APP.route('/channel/addowner/v1', methods=['POST']) 
def channel_addowner(): 
    return dumps(channel.channel_addowner(**request.get_json())) 
    
@APP.route('/channel/removeowner/v1', methods=['POST']) 
def channel_removeowner(): 
    return dumps(channel.channel_removeowner(**request.get_json())) 
    
@APP.route('/channel/leave/v1', methods=['POST']) 
def channel_leave(): 
    return dumps(channel.channel_leave(**request.get_json()))

@APP.route('/message/send/v2', methods=['POST'])
def message_send():
    return dumps(message.message_send(**request.get_json()))

@APP.route('/dm/leave/v1', methods=['POST'])
def dm_leave():
    return dumps(dm.dm_leave(**request.get_json()))

@APP.route('/dm/remove/v1', methods=['DELETE'])
def dm_remove():
    return dumps(dm.dm_remove(**request.get_json()))

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    return dumps(dm.dm_create(**request.get_json()))

@APP.route('/dm/invite/v1', methods=['POST'])
def dm_invite():
    return dumps(dm.dm_invite(**request.get_json()))

@APP.route('/dm/list/v1', methods=['GET'])
def dm_list():
    return dumps(dm.dm_list(request.args.get('token')))

@APP.route('/dm/details/v1', methods=['GET'])
def dm_details():
    return dumps(dm.dm_details(request.args.get('token'), int(request.args.get('dm_id'))))

@APP.route('/dm/messages/v1', methods=['GET'])
def dm_messages():
    return dumps(dm.dm_messages(request.args.get('token'), int(request.args.get('dm_id')), int(request.args.get('start'))))

@APP.route('/message/share/v1', methods=['POST'])
def message_share():
    return dumps(message.message_share(**request.get_json()))
    
@APP.route('/message/edit/v2', methods=['PUT'])
def message_edit():
    message.message_edit(**request.get_json())

@APP.route('/message/senddm/v1', methods=['POST'])
def message_senddm():
    return dumps(message.message_senddm(**request.get_json()))

@APP.route('/message/remove/v1', methods=['DELETE'])
def message_remove():
    return dumps(message.message_remove_v1(**request.get_json()))

@APP.route('/auth/register/v2', methods=['POST'])
def auth_register():
    return dumps(auth.auth_register(**request.get_json()))

@APP.route('/auth/login/v2', methods=['POST'])
def auth_login():
    return dumps(auth.auth_login(**request.get_json()))

@APP.route('/auth/logout/v1', methods=['POST'])
def auth_logout():
    return dumps(auth.auth_logout(**request.get_json()))
  
@APP.route('/user/profile/v2', methods=['GET'])
def user_profile():
    return dumps(user.user_profile(request.args.get('token'), int(request.args.get('u_id'))))
    
@APP.route('/user/profile/setname/v2', methods=['PUT'])
def user_profile_setname():
    return dumps(user.user_profile_setname(**request.get_json()))
    
@APP.route('/user/profile/setemail/v2', methods=['PUT'])
def user_profile_setemail():
    return dumps(user.user_profile_setemail(**request.get_json()))
    
@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def user_profile_sethandle():
    return dumps(user.user_profile_sethandle(**request.get_json()))
        
@APP.route('/users/all/v1', methods=['GET'])
def users_all():
    return dumps(user.users_all(request.args.get('token')))

@APP.route('/search/v2', methods=['GET'])
def search():
    return dumps(other.search(request.args.get('token'), request.args.get('query_string')))

@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_user_remove():
    return dumps(other.admin_user_remove(**request.get_json()))

@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_userpermission_change():
    return dumps(other.admin_userpermission_change(**request.get_json()))

@APP.route('/clear/v1', methods=['DELETE'])
def clear():
    return(other.clear())

@APP.route('/notifications/get/v1', methods=['GET'])
def notifications_get_v1():
    return dumps(other.notifications_get_v1(request.args.get('token')))
    
if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port
