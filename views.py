from sanic.response import redirect, text
# from sanja import render
from jinja2_sanic import template, render_template

from auth import check_credentials, create_user, get_nickname


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
    if await check_credentials(username, password):
        request.ctx.session['logged_in'] = True
        request.ctx.session['username'] = username
        request.ctx.session['nickname'] = await get_nickname(username)
        return redirect('/lobby')
    return redirect('/login?login_failed=True')


@template('register.html.j2')
async def register_get(request):
    if request.args.get('register_failed'):
        reason = request.args.get('reason')
        to_send = {'register_failed': True,
                   'reason': reason, }
        print(to_send)
        return to_send
    return {}


async def register_post(request):
    username = request.form.get('username')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    result = await create_user(username, password, nickname)
    if result == 'success':
        return redirect('/')
    else:
        return redirect(f'/register?register_failed=True&reason={result}')


@template('lobby.html.j2')
async def lobby(request):
    return {'': 23235}


# @render('room.html.j2', 'html')
@template('room.html.j2')
async def room(request, roomID):
    return {'roomID': roomID}
