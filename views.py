from sanic.response import redirect, text
# from sanja import render
from jinja2_sanic import template, render_template

from auth import (
    authenticate, create_user, get_nickname,
    ImproperNicknameError, ImproperUsernameError,
    NicknameDuplicateError, UsernameDucpliateError)


@template('index.html.j2')
async def index(request):
    if request.ctx.session.get('logged_in'):
        return {'logged_in': True}
    else:
        return {'logged_in': False}


@template('login_page.html.j2')
async def login_get(request):
    if request.args.get('login_failed'):
        return {'login_failed': True}
    return {}


async def login_post(request):
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        if await authenticate(username, password):
            request.ctx.session['logged_in'] = True
            request.ctx.session['username'] = username
            request.ctx.session['nickname'] = await get_nickname(username)
            return redirect('/lobby')
    except:
        return redirect('/login?login_failed=True')


@template('register.html.j2')
async def register_get(request):
    if request.args.get('register_failed'):
        reason = request.args.get('reason')
        data = {'register_failed': True,
                   'reason': reason, }
        return data
    return {}


async def register_post(request):
    username = request.form.get('username')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    try:
        await create_user(username, password, nickname)
        return redirect('/')
    except Exception as e:
        return redirect(f'/register?register_failed=True&reason={e.__class__.__name__}')


@template('lobby.html.j2')
async def lobby(request):
    return {'': 23235}


# @render('room.html.j2', 'html')
@template('room.html.j2')
async def room(request, roomID):
    return {'roomID': roomID}
