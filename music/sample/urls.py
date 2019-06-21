from django.urls import path
from sample import views

urlpatterns = [
    path(r'register/',views.register),
    path(r'login/',views.login),
    path(r'logout/',views.logout),
    path(r'',views.homepage),
    #path(r'song/<int:id>',views.song),
    #path(r'getAttr/', views.getAttr, name='getAttr'),
    path(r'mymusic/', views.mymusic),
    path(r'Search/',views.search),
    #path(r'detail/<str:table>/<str:key>/', views.detail, name='detail'),
    path(r'music_player_song/',views.music_player_song),
    path(r'get_music_detail/',views.get_music_detail),
    path(r'music_player_playlist/',views.music_player_playlist),
    path(r'single_playlist_info/',views.single_playlist_info),
    #path(r'mymusic/createlist/', views.createlist, name='createlist'),
    path(r'alterPlayList/', views.alterPlayList),
    path(r'remove_playlist/', views.remove_playlist),
    # path(r'getCreateList/', views.getCreateList),
    path(r'mymusic/createlist/', views.createlist),
    #path(r'alterSong/', views.alterSong),
    path(r'upload/', views.upload),
    path(r'ajax_songlist/',views.getsonglist),
    path(r'ajax_addsong/',views.add_song),
    path(r'ajax_removesong/',views.remove_song),
    path(r'ajax_addsonglist/',views. add_songlist),
    
]
 