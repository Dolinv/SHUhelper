# -*- coding: utf-8 -*-
"""
    application.auth.api
    ~~~~~~~~~~~~~~~~~~
    
"""
from flask import Blueprint, jsonify, g, request, abort,current_app
from application.extensions import limiter
from datetime import datetime
from application.models.user import User,SocialOAuth
from flask_login import login_required

import requests
import json
auth = Blueprint("auth", __name__)


@auth.before_request
def check_rate_limiting():
    """Check the the rate limits for each request for this blueprint."""
    return limiter.check()


@auth.errorhandler(429)
def login_rate_limit_error(error):
    """Register a custom error handler for a 'Too Many Requests'
    (HTTP CODE 429) error."""
    return jsonify(message='Too Many Requests')


def login_rate_limit():
    """Dynamically load the rate limiting config from the database."""
    # [count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
    return "50/30minutes"


def login_rate_limit_message():
    """Display the amount of time left until the user can access the requested
    resource again."""
    current_limit = getattr(g, 'view_rate_limit', None)
    if current_limit is not None:
        window_stats = limiter.limiter.get_window_stats(*current_limit)
        reset_time = datetime.utcfromtimestamp(window_stats[0])
        timeout = reset_time - datetime.utcnow()
    return "{timeout}".format(timeout=timeout)


# Activate rate limiting on the whole blueprint
limiter.limit(login_rate_limit, error_message=login_rate_limit_message)(auth)


@auth.route('/oauth/wx')
def get_open_id():
    s = requests.Session()
    code = request.args.get('code')
    source = request.args.get('source')
    appid = current_app.config['MP_OAUTH'][source]['appid']
    secret = current_app.config['MP_OAUTH'][source]['secret']
    r = s.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code'.format(appid, secret, code))
    auth_result = json.loads(r.text)
    if 'openid' in auth_result:
        open_id = auth_result['openid']
        auth_record = SocialOAuth.query(open_id=open_id).first()
        if auth_record is None:
            auth_record = SocialOAuth()
            auth_record.save()
        if auth_record.user_id is None:
            return jsonify(msg='请绑定一卡通',authID=auth_record.id),400
        user = auth_record.user
        token = user.generate_auth_token(864000)
        result = user.login(token)
        return jsonify(result)
    return jsonify(msg='error'), 401


@auth.route("/login", methods=['GET', 'POST'])
def login():
    """ main user auth view function
    user was authenticated when user has valid token (which stored in redis),
    or has valid cardID and password
    """
    if request.method == 'GET':
        token = request.args.get('token')
        user = User.verify_auth_token(token)
        if user is None:
            abort(401)
    else:
        auth_id = request.args.get('authID')
        json_post = request.get_json()
        user = User.query.get(json_post['id'])
        need_fresh = False
        if user is not None:
            need_fresh = not user.authenticate(json_post['password'])
        else:
            user = User(id=json_post['id'])
            need_fresh = True
        if need_fresh and not user.regisiter(json_post['password']):
            abort(403)
        if auth_id is not None:
            oauth_record = SocialOAuth.query(id=auth_id).first()
            if auth_id is None:
                return jsonify(msg='OAuth id 非法'),400
            oauth_record.bind_user(user.id)
        token = user.generate_auth_token(864000)
    result = user.login(token)
    return jsonify(result)