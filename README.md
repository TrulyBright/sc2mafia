# SC2 Mafia!

스타크래프트 2의 유명 아케이드 '-마피아-'를 웹게임으로 구현했습니다.
## 실행 방법(리눅스 기준)
1. 이 레포지토리를 복사합니다.
```
$ git clone https://github.com/TrulyBright/sc2mafia.git
```
2. SQLite3을 설치합니다.
```
$ sudo apt-get install sqlite3
```
3. redis를 설치합니다.
```
$ sudo apt-get install redis
```
4. 레포지토리를 복사한 디렉토리에 들어갑니다.
```
$ cd sc2mafia
```
5. 파이썬 패키지들을 설치합니다.
```
$ pip3 install -r requirements.txt
```
6. SQLite DB 스키마를 적용합니다.
```
$ sqlite3 sql/users.db < sql/schema.sql
```
7. 서버를 실행합니다.
```
$ python3 main.py
```
8. `localhost:8000`으로 접속하면 서버가 나옵니다.
## 알려진 버그

01. 첫날 원수/시장이 나올 수 있음
​
## 구현된 것들

## 구현 안된 것들

- 버스기사
- 변장자
- 밀고자
- 투표 종류(기명/무기명/재판/즉시사형) 선택 기능
