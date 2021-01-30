import aiosqlite
from sanic.response import redirect, text

# from sanja import render
from jinja2_sanic import template, render_template

from auth import (create_user,
                  ImproperNicknameError,
                  NicknameDuplicateError,
                  NicknameTooLongError,
                  getUserByNaverId)


@template("index.html.j2")
async def index(request):
    if request.ctx.session.get("logged_in"):
        return {"logged_in": True}
    else:
        return {"logged_in": False}

@template('callback.html.j2')
async def callback(request):
    return {}

async def login(request):
    client = request.app.oauth_client
    access_token = request.args.get('access_token').split('.')[1]
    print(access_token)
    url = 'https://openapi.naver.com/v1/nid/me'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    async with client.get(url, headers=headers) as r:
        result = await r.json()
        if result['resultcode']!='00':
            return text('로그인에 실패했습니다.')
    naverId = result['response']['id']
    user = await getUserByNaverId(naverId)
    if user is None:
        return redirect(f'/register?access_token={access_token}')
    request.ctx.session['nickname'] = user[2]
    request.ctx.session['is_superuser'] = user[3]
    request.ctx.session['disabled'] = user[4]
    request.ctx.session['logged_in'] = True
    return redirect('/game')

@template("register.html.j2")
async def register_get(request):
    if request.args.get("register_failed"):
        reason = request.args.get("reason")
        data = {
            "register_failed": True,
            "reason": reason,
        }
        return data
    return {}


async def register_post(request):
    client = request.app.oauth_client
    nickname = request.form.get('nickname')
    access_token = request.form.get('access_token')
    url = 'https://openapi.naver.com/v1/nid/me'
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    async with client.get(url, headers=headers) as r:
        result = await r.json()
        if result['resultcode']!='00':
            return redirect('/register?register_failed=True&reason=access_token_not_valid')
    naverId = result['response']['id']
    try:
        await create_user(naverId, nickname)
        return redirect('/')
    except (ImproperNicknameError, NicknameDuplicateError, NicknameTooLongError) as e:
        return redirect(f'/register?register_failed=True&reason={e.__class__.__name__}&access_token={access_token}')


@template('main.html.j2')
async def main(request):
    return {}


@template("archive.html.j2")
async def archive(request, gamelog_id):
    if not gamelog_id.isalnum(): return
    async with aiosqlite.connect("sql/records.db") as DB:
        cursor = await DB.execute(f"SELECT * FROM {gamelog_id};")
        log = await cursor.fetchall();
        return {"log": log}
