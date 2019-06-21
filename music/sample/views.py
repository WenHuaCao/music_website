import json
from datetime import date, datetime

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sample.models import user
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.shortcuts import render
from django.utils import timezone
from sample.models import Song,Playlist
from django.views.decorators.csrf import csrf_exempt
from mutagen.mp3 import MP3


from django.db.utils import IntegrityError
# Create your views here.

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

'''注册功能'''
@csrf_exempt
def register(request):
    flag = True
    alertBool = 0
    if request.method =="GET":
        return render(request,"Register.html")
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        if username == None or username == "" :
            alertBool = 1
            return render(request,"Register.html",{"alertBool":alertBool})
            flag = False
        if password== None or password == "":
            alertBool = 2
            return render(request,"Register.html",{"alertBool":alertBool})
            flag = False
        if password2 == None or password2 == "":
            alertBool = 3
            return render(request,"Register.html",{"alertBool":alertBool})
            flag  = False
        if flag :
            try:
                theuser = user.objects.create_user(username = username,
                                               password = password,
                                               issinger = 1,
                                               ismanger = 1,)
                Playlist.objects.create(
                    playlistname = str(username)+"_发布的音乐",
                    build_user = theuser,
                    picture_url = "/static/system_image_file/发布的音乐.jpg"
                    )
                Playlist.objects.create(
                    playlistname = str(username)+"_喜欢的音乐",
                    build_user = theuser,
                    picture_url = "/static/system_image_file/喜欢的音乐.jpg"
                    )
            except (IntegrityError) as e:
                print(e)
                error[0]= "用户名重复"
                flag = False
        if flag:
            auth.login(request, theuser)
            return HttpResponseRedirect(r'/')

'''登陆功能'''
def login(request):
    flag = True
    alertBool = 0
    if request.method =="GET":
        return render(request,"SignIn.html",{'alertBool': 0})
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    print(username, password)
    if(username == None or username == ""):
        alertBool = 1
        return render(request,"SignIn.html",{'alertBool': 1})
    if(password == None or password == ""):
        alertBool = 2
        return render(request,"SignIn.html",{'alertBool': 2})
    theuser = auth.authenticate(username=username, password=password)
    if theuser is None:
        alertBool = 3
        return render(request,"SignIn.html",{'alertBool': 3})
    auth.login(request, theuser)
    return HttpResponseRedirect(r'/')

'''跳转主页'''
def homepage(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(r'/login/')
    recommendData = recommend_music()
    return render(request,"index.html",{
        "username": request.user.username,
        "style0":"nav_hover",
        "recommendData": recommendData,
    })

def recommend_music():#首页推荐三个歌单
    list_result=[]
    playlists = list(Playlist.objects.all().values())[-3:]
    for each_list in playlists:
        dict_list = {}
        print("【测试显示】歌单ID：")
        print(each_list["id"])
        dict_list.update({"list_id":each_list["id"]})
        dict_list.update({"list_name":each_list["playlistname"]})
        dict_list.update({"list_picture":each_list["picture_url"]})
        list_result.append(dict_list)
    
    print("【测试显示】1")
    print(list_result)
    return list_result

'''注销功能'''
@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(r'/login/')

'''我的音乐界面'''
@login_required
def mymusic(request, success=4):          
    theuser = request.user
    collect = theuser.collect_user.all()
    build = theuser.build_user.all()
    collect_list = list(collect.values())
    build_list = list(build.values())

    collect_result=[]
    for each in collect_list:
        print("【测试显示】")
        print(each)
        dict_collect = {}
        dict_collect.update({"id":each["id"]})
        dict_collect.update({"playList_name":each["playlistname"]})
        dict_collect.update({"playlist_createdTime":str(each["build_date"])})
        play=Playlist.objects.filter (id = each["id"])
        song_num = len(play[0].songs.all().values())
        dict_collect.update({"playlist_cnt":song_num})
        collect_result.append(dict_collect)

    build_result=[]
    for each in build_list:
        dict_build = {}
        dict_build.update({"id":each["id"]})
        dict_build.update({"playList_name":each["playlistname"]})
        dict_build.update({"playlist_createdTime":str(each["build_date"])})
        play=Playlist.objects.filter (id = each["id"])
        song_num = len(play[0].songs.all().values())
        dict_build.update({"playlist_cnt":song_num})
        build_result.append(dict_build)

    print(build_result)
    print(collect_result)
    return render(request, 'playlist.html', {
        #'username': request.user.username,
        'build_result': build_result,
        'collect_result': collect_result,
        "style1":"nav_hover",
        'success': success,  
    })

'''搜索结果界面'''
@login_required
def search(request):

    value = request.GET.get("value",None)
    songs_result = search_music(value)
    #print(result)
    username = request.user.username
    playlists_result = search_playlist(username,value)
    return render(request, 'Search.html', {
        #'username': request.user.username,
        'value': value,
        'songs_result': songs_result,
        'playlists_result' : playlists_result
    })

def search_music(value):
    songs = Song.objects.filter (songname__icontains=value)
    temp_result = list(songs.values())
    #print("【测试显示】")
    songs_result=[]
    for each_song in temp_result:
        dict_song = {}
        dict_song.update({"song_id":each_song["id"]})
        dict_song.update({"songList_songname":each_song["songname"]})
        dict_song.update({"songList_songauthor":each_song["singer"]})
        dict_song.update({"songList_album":each_song["album_name"]})
        temp = each_song["song_time"]
        time = str(int(float(temp)/60)) + ':' + str(int(float(temp))%60)
        dict_song.update({"songList_songtime":time})
        songs_result.append(dict_song)
    return songs_result

def search_playlist(username,value):
    playlists = Playlist.objects.filter (playlistname__icontains=value)
    playlists_result = []
    tmep_playlists_result = list(playlists.all().values())
    for each_playlist in tmep_playlists_result:
        dict_playlist = {}
        dict_playlist.update({"playlist_id":each_playlist["id"]})
        dict_playlist.update({"songListT_name":each_playlist["playlistname"]})

        play=Playlist.objects.filter (id = each_playlist["id"])
        song_num = len(play[0].songs.all().values())

        dict_playlist.update({"songListT_num":song_num})
        dict_playlist.update({"songList_songauthor":play[0].build_user.username})
        if len(play[0].collectuser.all().filter(username=username)) > 0:
            # 已收藏
            dict_playlist.update({"playlist_flag":"1"})
        else:
            # 未收藏
            dict_playlist.update({"playlist_flag":"0"})
        playlists_result.append(dict_playlist)
    return playlists_result


@login_required
def music_player_song(request):
    value = request.GET.get("value")
    songid = request.GET.get("songid")
    songs_result=search_music(value)
    return render(request, 'music_player.html', {
        #'username': request.user.username,
        'songid' : songid,
        'songs_result': songs_result,
    })

@login_required
def music_player_playlist(request):
    playlistid = request.GET.get("playlistid")
    songid = request.GET.get("songid")
    p = Playlist.objects.filter (id=playlistid)
    playlist = p.all().values()[0]
    songs = list(p[0].songs.all().values())
    songs_result=[]
    for each_song in songs:
        dict_song = {}
        dict_song.update({"song_id":each_song["id"]})
        dict_song.update({"songList_songname":each_song["songname"]})
        dict_song.update({"songList_songauthor":each_song["singer"]})
        dict_song.update({"songList_album":each_song["album_name"]})
        temp = each_song["song_time"]
        time = str(int(float(temp)/60)) + ':' + str(int(float(temp))%60)
        dict_song.update({"songList_songtime":time})
        songs_result.append(dict_song)
    
    return render(request, 'music_player.html', {
        #'username': request.user.username,
        'songid' : songid,
        'songs_result': songs_result,
    })

@login_required
def single_playlist_info(request):
    playlistid = request.GET.get("id")
    p = Playlist.objects.filter (id=playlistid)
    playlist = p.all().values()[0]

    # 歌单相关字典
    playlists_result = []
    dict_playlist = {}
    dict_playlist.update({"playlist_id":playlist["id"]})
    dict_playlist.update({"playList_name":playlist["playlistname"]})
    dict_playlist.update({"playList_date":str(playlist["build_date"])})
    dict_playlist.update({"picture_url":playlist["picture_url"]})

    song_num = len(p[0].songs.all().values())
    dict_playlist.update({"playList_num":song_num})
    dict_playlist.update({"playList_build_user":p[0].build_user.username})
    playlists_result.append(dict_playlist)

    # 歌曲相关字典
    songs = list(p[0].songs.all().values())
    songs_result=[]
    for each_song in songs:
        dict_song = {}
        dict_song.update({"song_id":each_song["id"]})
        dict_song.update({"songList_songname":each_song["songname"]})
        dict_song.update({"songList_songauthor":each_song["singer"]})
        dict_song.update({"songList_album":each_song["album_name"]})
        temp = each_song["song_time"]
        time = str(int(float(temp)/60)) + ':' + str(int(float(temp))%60)
        dict_song.update({"songList_songtime":time})
        songs_result.append(dict_song)
    
    return render(request, 'single_playlist_info.html', {
        'playlists_result': playlists_result,
        'songs_result': songs_result,
    })
'''上传界面'''
@login_required
def upload(request):
    #len_id = Song.objects.get(songname = list(Song.objects.all())[-1]).id + 1
    error = ['','','','上传音乐文件','上传歌词文件','上传配图文件']
    flag = True
    if request.method == "POST":
        songname = ""
        singer = ""
        words = ""
        song_url = ""
        picture_url = ""
        album_name = ""
        song_time = 0
        songname = request.POST.get("songname",None)  #输入歌曲名
        singer = request.POST.get("singer",None) #输入歌手名
        album_name = request.POST.get("album_name",None) #输入专辑名
        #获取歌曲文件
        song_file = request.FILES.get("song_file",None)
        #获取歌词文件
        song_words_file = request.FILES.get("song_words_file",None)
        #获取图片文件
        picture_file = request.FILES.get("picture_file",None)
        #判断输入是否出错
        if album_name == None or album_name == "":
            error[0] = "专辑名不能为空"
            flag = False
        if songname == None or songname == "":
            error[1] = "歌名不能为空"
            flag = False
        if singer == None or singer == "":
            error[2] = "歌手名不能为空"
            flag = False
        if song_file == None or song_file.name[-4:]!=".mp3":
            error[3] = "歌曲文件未选择或格式不为MP3"
            flag = False
        if song_words_file == None or song_words_file.name[-4:]!=".txt":
            error[4] = "歌词txt文件未选择或格式不为txt"
            flag = False
        if picture_file == None:
            error[5] = "歌曲配图文件未选择"
            flag = False
        #按要求输入相关数据和文件后进行数据处理
        if flag:
            thesong = Song.objects.create(
                    songname = songname,
                    singer = singer,
                    album_name = album_name,
                    words = "words",
                    song_url = "song_url",
                    picture_url = "picture_url",
                    song_time = "song_time",
                    userid = request.user
                )
            id=thesong.id
            #歌曲文件及路径名
            file_name_song = "./static/song_file/" + str(id) + "_" + song_file.name
            #歌词文件及路径名
            file_name_song_words = "./static/song_words_file/" + str(id) + "_" + song_words_file.name
            #图片文件及路径名
            file_name_picture = "./static/picture_file/" + str(id) + "_" + picture_file.name
            picture_url = file_name_picture
            song_url = file_name_song
            #分块写入文件
            with open(file_name_song, mode='wb+') as f:
                for chunk in  song_file.chunks():
                    f.write(chunk)
            with open(file_name_song_words, mode='wb+') as f:
                for chunk in  song_words_file.chunks():
                    f.write(chunk)
            with open(file_name_picture, mode='wb+') as f:
                for chunk in  picture_file.chunks():
                    f.write(chunk)
            #读取歌词存为string
            for line in  open(file_name_song_words):
                line = line.strip('\n')
                words = words+line+"\n"
            #获取音乐时长
            audio = MP3(song_url)
            song_time = str(audio.info.length)
            #创建model
            thesong = Song.objects.filter(id=id).update(
                    #songname = songname,
                    #singer = singer,
                    #album_name = album_name,
                    words = words,
                    song_url = song_url[1:],
                    picture_url = picture_url[1:],
                    song_time = song_time
                )
            #插入到默认歌单：我发布的音乐
            thesong = Song.objects.get(id=id)
            playlist = Playlist.objects.get(playlistname=str(request.user.username)+"_发布的音乐")
            playlist.songs.add(thesong)
            return render(request, 'upload.html', {
                'alertBool': 1,
                'username': request.user.username,
                })
        else:
            return render(request, 'upload.html', {
                    'alertBool': 0,
                    'username': request.user.username,
                })
    else:
        return render(request, 'upload.html', {
                    'username': request.user.username,
                    'alertBool': 2,
                    "error": error,
                    "style2":"nav_hover"
                })
        #return render(request,"upload.html",{"error": error})
'''
@login_required
def getAttr(request):
    func = request.GET.get('func', None)
    attr = request.GET.get('attr', None)
    value = request.GET.get('value', None)
    playlist = request.GET.get('playlist', None)
    username = request.GET.get('username', None)
    attrs = eval('%s.getattr()' % func)

    if playlist is not None:
        result = eval('%s.getItems(username, attr, value, playlist)' % func)
    else:
        result = eval('%s.getItems(username, attr, value)' % func)

    jsondata = {'attrs': attrs, 'result': result, 'table': func}
    return JsonResponse(jsondata)
'''
'''传入songid，得到songid的具体信息'''
@login_required
def get_music_detail(request):
    songid = request.GET.get('id', None)
    result = list(Song.objects.filter(id=songid).values())

    songname = result[0]['songname']
    album_name = result[0]['album_name']
    song_url = result[0]['song_url']
    words = result[0]['words']
    picture_url = result[0]['picture_url']

    jsondata = {
            'songname': songname,
            'album_name': album_name,
            'song_url': song_url,
            'words':words,
            'picture_url': picture_url
            }
    print(words)  
    return JsonResponse(jsondata, json_dumps_params={'ensure_ascii':False})

'''传入playlistid 得到歌单的详细信息'''
@login_required
def playlist(request):
    playlistid = request.GET.get('playlistid', None)
    p = Playlist.objects.filter(id=playlistid)
    playlist = p.all().values()[0]
    songs = list(p[0].songs.all().values())
    playlist['build_user'] = p[0].build_user.username
    playlist['songs_counts'] = len(songs)
    playlist['songs'] = json.dumps(songs, cls=ComplexEncoder)
    playlist['attrs'] = Song.getattr()
    return render(request, 'playlist.html', {
        'username': request.user.username,
        'playlist': playlist,
    })

'''创建歌单'''
@login_required
def createlist(request):
    if request.method == 'POST':
        playlistname = request.POST.get('playlistname', None)
        build_user = request.user
        picture_file = request.FILES.get("picture_file",None)
        pl = Playlist.objects.filter(playlistname=playlistname,build_user=request.user)
        if len(pl) != 0:
            message = '歌单名已存在，请重新输入！'
            return render(request, 'createlist.html', {
                'alertBool': 0,
                'username': request.user.username,
                'message': message,
            })
        #创建歌单
        thelist = Playlist.objects.create(
            playlistname = playlistname,
            picture_url = "",
            build_user = build_user,
        )
        id = thelist.id
        file_name_picture = "./static/playlist_picture_file/" + str(id) + "_" + picture_file.name
        picture_url = file_name_picture
        #写入文件
        with open(file_name_picture, mode='wb+') as f:
            for chunk in  picture_file.chunks():
                f.write(chunk)
        #更新歌单图片路径
        thelist = Playlist.objects.filter(id=id).update(
            #playlistname = playlistname,
            picture_url = picture_url[1:],
            #build_user = build_user,
        )
        return mymusic(request, 3)
    return render(request, 'createlist.html', {
        'alertBool': 2,
        'username': request.user.username,
    })

@login_required
def remove_playlist(request):
    flag = 0
    listid = request.GET.get("id",None)
    playlist = Playlist.objects.get(id = listid)
    if playlist.build_user == request.user:  #删除用户自建的歌单
        '''前端要做，如果是在自建歌单里，发布的音乐和喜欢的音乐后不显示删除按钮'''
        if playlist.playlistname == str(request.user.username)+"_发布的音乐" or playlist.playlistname == str(request.user.username)+"_喜欢的音乐":
            print("【无法删除系统默认创建歌单】")
            return mymusic(request, 0)
        else:
            playlist.delete()
            return mymusic(request, 1)
    elif request.user in list(playlist.collectuser.all()): #删除用户收藏的歌单
        print("【移除了用户"+str(request.user.username)+"收藏的"+str(playlist.playlistname))
        playlist.collectuser.remove(request.user)
        return mymusic(request, 2)



#前置条件：用户点击收藏某首歌曲的时候，返回用户自己创建的所有的歌单
#后置条件：排除上传歌单,默认一个用户创建的歌去的名称可以唯一决定该歌曲的id
@login_required
def getsonglist(request):
    theuser = request.user
    print("this")
    build = Playlist.objects.filter(build_user = theuser).exclude(playlistname = "%s_发布的音乐"%theuser.username)
    result = [{"play_listid":x.id,"list_img":x.picture_url,"list_num":len(list(x.songs.all())),"list_name":x.playlistname} for x in build]
    return JsonResponse( result,safe=False,json_dumps_params={'ensure_ascii':False})
#添加歌曲到自己建立的歌单
#判断歌单是否是用户所创建

@login_required
def remove_song(request):
    theuser = request.user
    songid =  request.GET.get('songid', None)
    songlistid =  request.GET.get('songlistid', None)
    if songid == None or  songlistid == None:
        return JsonResponse({"message":"参数错误","status":0} ,json_dumps_params={'ensure_ascii':False})
    song = Song.objects.get(id = songid ) #歌曲
    songlist = Playlist.objects.get(id = songlistid) #歌单
    if theuser != songlist.build_user:
        return JsonResponse({"message":"这不是您创建的歌单，您没有权限!","status":0},json_dumps_params={'ensure_ascii':False})
    if song  in songlist.songs.all():
        songlist.songs.remove(song)
        return JsonResponse({"message":"您成功将歌曲在歌单 %s 内删除 !"%songlist.playlistname ,"status":1},json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"message":"该歌曲不在歌单内 %s"%songlist.playlistname ,"status":1},json_dumps_params={'ensure_ascii':False})

@login_required
def add_song(request):
    theuser = request.user
    songid =  request.GET.get('songid', None)
    songlistid =  request.GET.get('songlistid', None)
    if songid == None or  songlistid == None:
        return JsonResponse({"message":"参数错误","status":0} ,json_dumps_params={'ensure_ascii':False})
    song = Song.objects.get(id = songid ) #歌曲
    songlist = Playlist.objects.get(id = songlistid) #歌单
    if theuser != songlist.build_user:
        return JsonResponse({"message":"这不是您创建的歌单，您没有权限!","status":0},json_dumps_params={'ensure_ascii':False})
    if song not in songlist.songs.all():
        songlist.songs.add(song)
        return JsonResponse({"message":"您成功将歌曲添加入歌单：%s !"%songlist.playlistname ,"status":1},json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"message":"歌单： %s已存在该收藏歌曲"%songlist.playlistname ,"status":1},json_dumps_params={'ensure_ascii':False})


#添加
@login_required
def add_songlist(request):
    theuser = request.user
    songlistid = request.GET.get("songlistid",None)
    if songlistid == None:
        return JsonResponse({"message":"parameters errors"})
    songlist = Playlist.objects.get(id = songlistid)
    if theuser in songlist.collectuser.all():
        songlist.collectuser.remove(theuser)
        print("删除")
        return JsonResponse({"message":"你已取消收藏该歌单"})
    else:
        print("添加")
        songlist.collectuser.add(theuser)
        return JsonResponse({"message":"你成功收藏改该歌单"})


'''歌单添加删除歌曲'''
@login_required
def alterSong(request):
    song_name = request.GET.get('song_name', None)
    list_name = request.GET.get('list_name', None)
    action = request.GET.get('action', None)
    
    # print(song_name)

    song = Song.objects.get(songname=song_name)
    playlist = Playlist.objects.get(playlistname=list_name)
    
    if action == '1':
        # 添加联系
        if song not in playlist.songs.all():
            playlist.songs.add(song)
    else:
        # 删除联系
        if song in playlist.songs.all():
            playlist.songs.remove(song)

    return JsonResponse({'Action': ('Add' if action=='1' else 'Delete'), 'result': 'Success'})

'''收藏或者取消收藏歌单'''
@login_required
def alterPlayList(request):
    #username = request.GET.get('username', None)
    playlist = request.GET.get('playlist', None)
    action = request.GET.get('action', None)
    user = request.user
    playlist = models.Playlist.objects.get(playlistname=playlist)
        
    if action == '1':
        # 添加联系
        if user not in playlist.collectuser.all():
            playlist.collectuser.add(user)
    else:
        # 删除联系
        if user in playlist.collectuser.all():
            playlist.collectuser.remove(user)

    return JsonResponse({'Action': ('Add' if action=='1' else 'Delete'), 'result': 'Success'})


