from django.urls import path
from. import views
from django.contrib.sitemaps.views import sitemap
from musicapp.sitemaps import *
from django.views.generic.base import TemplateView

sitemaps ={
    "static":StaticSitemap,
    "postsitemap":PostSitemap
    
}

urlpatterns = [
    path("robots.txt/", TemplateView.as_view(template_name = "robots.txt", content_type = "text/plain")),
    path("sitemap.xml/", sitemap, {"sitemaps":sitemaps}, name= "django.contrib.sitemaps.views.sitemap"),
    path("", views.index, name ="index"),
    path("all-songs/", views.allposts, name="all_songs"),
    path("posts/<slug>/",views.postdetails, name="post_details"),
    path("search/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("upload-song/", views.musician_upload_with_branded_image, name="musicianuploadsong"),
    path("profile/", views.artistprofile, name="profile"),
    path("all-artist-songs/", views.all_artist_songs, name="all_artist_songs"),
    path("songs/<str:username>/", views.songs, name="songs"),
    path("change-password", views.change_password, name="change_password"),
    path("edit-profile/", views.editprofile, name="edit_profile"),
    path("edit-coverimage/", views.editcoverimage, name="edit_coverimage"),
    path("change-password",views.change_password, name="change_password"),
    # path("song-play-count/<int:song_id>/", views.songplay_count, name="songplay_count"),
    path("song_download/<int:song_id>/", views.download_song, name="download_song"),
    path("increment-download/<int:song_id>/", views.increement_download_count, name="download_count"),
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('addtoplaylist/<song_id>/', views.addsongtoplaylist, name='addtoplaylist'),
    ###################################### PREMIUM USERS URLS ###########################################################
    path("upgrade/",views.upgradetopremium, name="upgradetopremium"),
    path("create-album/", views.create_album, name="create_album"),

    ###################################### PREMIUM USERS URLS end  ###########################################################

    ###################################### Static Pages URLS ###########################################################
    path("contact-us/",views.contact_us, name="contact_us"),
    path("about-us/",views.about_us, name="about_us"),
    path("terms-and-conditions/",views.termconditions, name="terms"),
    path("disclaimer/",views.disclaimer, name="disclaimer"),
    path("privacy/",views.privacy, name="privacy"),
    ###################################### Static Pages URLS end ###########################################################
    path('branded-dp/', views.branded_dp_generator, name='branded_dp_generator'),   
    path("new-branded/", views.musician_upload_with_branded_image, name="new-branded")
   
    
   
]
