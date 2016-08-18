import time
from flask import abort, Flask, jsonify, request
from . import api
from ..models import Developer, Integration
import jpush
from jpush import common


@api.route('/message/<integration_id>/<token>', methods=['POST'])
def send_message(integration_id, token):
    if not request.json or not 'message' in request.json or not 'title' in request.json:
        abort(400)
    integration = Integration.verify_auth_token(token)
    print(dir(integration))
    if integration is None:
        abort(404)
    # channel dev_ID
    developer = Developer.query.filter_by(id=integration.developer_id).first()
    print(dir(developer))
    if developer is None:
        abort(404)

    _jpush = jpush.JPush(u'a1703c14b186a68a66ef86c1', u'9dabdf8bb704b421759cb49c')
    push = _jpush.create_push()
    _jpush.set_logging("DEBUG")
    push.audience = jpush.audience(
        jpush.tag(developer.dev_key + integration.channel)
    )
    # push.audience = jpush.all_
    # push.notification = jpush.notification(alert=request.json['title'],extras={'title': request.json['title'],
    #                                                                              'message': request.json['message']})
    android_msg = jpush.android(alert=request.json['title'], extras={'title': request.json['title'],
                                                                     'message': request.json['message']})
    ios_msg = jpush.ios(alert=request.json['title'], extras={'title': request.json['title'],
                                                             'message': request.json['message']})
    # ios_msg = jpush.ios(alert=request.json['title'], extras={'title': request.json['title']})
    push.notification = jpush.notification(alert=request.json['title'], android=android_msg, ios=ios_msg)
    push.message = jpush.message(msg_content=request.json['message'], title=request.json['title'],
                                 extras={'dev_key': developer.dev_key, 'channel': integration.channel,
                                         'datetime': int(time.time())})
    push.options = {"time_to_live": 86400, "sendno": 12345, "apns_production": False}
    push.platform = jpush.all_
    try:
        response = push.send()
        print(response)
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn error")
    except common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")
    return jsonify({}), 200
