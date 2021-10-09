from pymongo import MongoClient

client = None
db = None


def connMongDB():
    global client, db
    client = MongoClient('localhost', 27017)
    db = client['hbot']

    # 만약 플레이리스트의 수를 새어주는 DB가 없다면 만들어 저장
    if not db['count'].find_one({'name' : 'playlist_count'}):
        data = {
            'name' : 'playlist_count',
            'cnt' : 0
        }

        db['count'].insert_one(data)


# MongoDB에 접근하여 플레이리스트 저장
def savePlayList(id, title, url, collection):
    connMongDB()

    playlist_count = db['count'].find_one({'name' : 'playlist_count'})
    cnt = playlist_count['cnt']

    # id가 DB에 저장되어 있지 않다면 새로 만들어서 저장
    if not db[collection].find_one({'user_id' : id}):
        data = {
            'user_num' : cnt + 1,
            'user_id' : id,
            'playlist' : [[title, url]]
        }

        db[collection].insert_one(data)
        db['count'].update(
            {'name' : 'playlist_count'},
            {'$set': {'cnt' : cnt + 1}}
        )


    else:
        user_data = db[collection].find_one({'user_id' : id})

        play = user_data['playlist']
        play.append([title, url])

        db[collection].update(
            {'user_id' : id},
            {'$set': {
                'playlist' : play,
                'user_num' : cnt + 1
                }
            }
        )
        
    return '[%s] 저장이 완료되었습니다.' % title