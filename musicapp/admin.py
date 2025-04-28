from django.contrib import admin
from .models import (User,Post,trendingsongs,promotedsongs,Comment,replycomment,SongPlay,SongDownload,Playlist, PlaylistSong, Artist)

admin.site.register(User)
admin.site.register(Post)
admin.site.register(trendingsongs)
admin.site.register(promotedsongs)
admin.site.register(Comment)
admin.site.register(replycomment)
admin.site.register(SongDownload)
admin.site.register(SongPlay)
admin.site.register(Playlist)
admin.site.register(PlaylistSong)
admin.site.register(Artist)


############################################# PREMIUM MODELS ##########################################################
from .models import(PremiumUser, Album,Userbrandedimage)


admin.site.register(PremiumUser)
admin.site.register(Album)
admin.site.register(Userbrandedimage)

