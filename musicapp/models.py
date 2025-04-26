from django.db import models
from django.contrib.auth.models import AbstractUser
from django. urls import reverse
import hashlib #  for avoiding duplicate media
from PIL import Image
import os
from django.conf import settings
from django.contrib.staticfiles import finders
import requests
from io import BytesIO



class User(AbstractUser):
   email = models.EmailField(null =True, unique=True, max_length=100)
   address=models.CharField(max_length=255,null=True,blank=True)
   date_registered = models.DateTimeField(auto_now_add=True, null=True)
   reffered_by = models.ForeignKey("self", on_delete= models.CASCADE, blank=True, related_name="refferals",null=True)
   referal_wallet = models.DecimalField(max_digits=10, decimal_places= 2, default= 0.00)
   image = models.ImageField(upload_to="images",null=True, blank= True)
   cover_image = models.ImageField(upload_to="images",null=True, blank= True)
   referal_link = models.CharField(max_length=40, null =True)


# become a premium user

#creating categories
class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name




#creating blog posts
class Post(models.Model):
    STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    )
    Genres_choices = (
         ("Gospel", "Gospel"),
         ("R&B", "R&B"),
         ("Pop", "Pop"),
         ("Rock", "Rock"),
         ("Jazz", "Jazz"),
         ("Country", "Country"),
         ("Reggae", "Reggae"),
         ("Blues", "Blues"),
         ("Others", "Others"),
         ("Electronic", "Electronic"),
         
         
    )
    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    title = models.CharField(max_length=255,null=True,blank=True)
    body = models.TextField(null=True)
    published= models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories', null=True,blank=True) 
    image=models.ImageField(upload_to="images",null=True)
    branded_image = models.ImageField(upload_to='images', blank=True)

    slug = models.SlugField(default="",max_length=200,unique=True, blank=True)#slug for urls
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
       default='published')
    upload_song = models.FileField(upload_to="audio",null=True,unique=True)
    meta_keywords = models.CharField(max_length=255,help_text='Comma-delimited set of SEO keywords for meta tag',null=True) 
    meta_description = models.CharField(max_length=255,help_text='Content for description meta tag',null=True)
    genres = models.CharField(max_length=50,choices= Genres_choices, default="Others")
    play_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    file_hash = models.CharField(max_length=64, unique = True, blank=True)
    image_hash = models.CharField(max_length=64, unique = True, blank=True)
   

    def save(self, *args,**kwargs ):
        if self.upload_song:
           hasher = hashlib.md5()
           for chunk in self.upload_song.chunks():
               hasher.update(chunk)
               self.file_hash = hasher.hexdigest()
                #check for duplicate
               if Post.objects.filter(file_hash = self.file_hash).exclude(pk = self.pk).exists():
                    raise ValueError ("This Song Already Exist")
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     if self.image:
    #         self.apply_frame_from_url()
    # def apply_frame_from_url(self):
    #     # Uploaded image path (your artist's image)
    #     cover_path = self.image.path

    #     # URL of the external frame image
    #     frame_url="http://127.0.0.1:8000/media/images/frame.jpg"

    #     # Download the frame image
    #     response = requests.get(frame_url)
    #     if response.status_code != 200:
    #         raise Exception("Failed to download frame image")

    #     frame_image = Image.open(BytesIO(response.content)).convert("RGBA")

    #     # Open the artist's image
    #     with Image.open(cover_path).convert("RGBA") as cover:
    #         cover = cover.resize(frame_image.size)
    #         combined = Image.alpha_composite(cover, frame_image)

    #         # Output path
    #         output_dir = os.path.join(settings.MEDIA_ROOT, 'branded_covers')
    #         os.makedirs(output_dir, exist_ok=True)
    #         output_path = os.path.join(output_dir, f'branded_{os.path.basename(cover_path)}')
    #         combined.save(output_path)

    #         # Save result to model field
    #         self.branded_image.name = f'branded_covers/branded_{os.path.basename(cover_path)}'
    #         super().save(update_fields=['branded_image'])

       
    class Meta: 
        verbose_name_plural="Posts"

    def __str__(self):
        return self.title
    #the slug to article details
    def get_absolute_url(self):
        return reverse("post_details", kwargs={"slug": self.slug})    
    

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete= models.CASCADE, null=True, related_name="postcomment")
    name = models.CharField(max_length=200, null=True)
    content = models.TextField(null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.name} commented on {self.post}"

class replycomment(models.Model):
    comment = models.ForeignKey(Comment, null=True, on_delete=models.CASCADE, related_name="replycomm")
    name = models.CharField(max_length=200, null=True)
    content = models.TextField(null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.name} reply on {self.comment} "
    
    #promoted songs
class promotedsongs(models.Model):
    post = models.ForeignKey(Post,on_delete= models.CASCADE, null=True, related_name="promotedsong")
    slug = models.SlugField(default="",max_length=200,unique=True)#slug for urls
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return f"{self.post.title} promoted"
    
#popular posts
class popularpost(models.Model):
    post = models.ForeignKey(Post,on_delete= models.CASCADE, null=True, related_name="popularposts")
    slug = models.SlugField(default="",max_length=200,unique=True)#slug for urls
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __(self):
        return f"{self.post} "

class trendingsongs(models.Model):
    post = models.ForeignKey(Post,on_delete= models.CASCADE, null=True, related_name="trendingsongs")
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.post}"
    
# newsletter subscription

class newsletter(models.Model):
    email = models.EmailField(null=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.email} subscribed to newsletter'
   
# SongPlay model to track the number of plays
class SongPlay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="usersongplay")
    song = models.ForeignKey(Post, on_delete=models.CASCADE,null=True, related_name="songplay")
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} played {self.song.title} at {self.played_at}"
    
# SongDownload model to track the number of downloads
class SongDownload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="usersongdownload")
    song = models.ForeignKey(Post, on_delete=models.CASCADE,null=True, related_name="songdownload")
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downloaded {self.song.title} at {self.downloaded_at}"
    
# songlikes

class songlike(models.Model):
    song = models.ForeignKey(Post, on_delete=models.CASCADE,null=True, related_name="songlike")
    like = models.BooleanField (default=False,null=True)
    
    def __str__(self):
        return f"{self.like} on {self.song}"

class Playlist(models.Model):
    user = models.ForeignKey(User, related_name="playlistuser", on_delete=models.CASCADE, null=True)
    name= models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} Playlist By {self.user}"

class PlaylistSong(models.Model):
    user = models.ForeignKey(User, related_name="playlists", on_delete=models.CASCADE, null=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    songs = models.ForeignKey(Post, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'songs')
    def __str__(self):
        return f"{self.songs.title} in {self.playlist.name}"

    

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

######################################### PREMIUM USERS ONLY #########################################################

class PremiumUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="premiumuser")
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.user} is a premium user"

class Album(models.Model):
    Album_Genres_choices = (
         ("Gospel", "Gospel"),
         ("R&B", "R&B"),
         ("Pop", "Pop"),
         ("Rock", "Rock"),
         ("Jazz", "Jazz"),
         ("Country", "Country"),
         ("Reggae", "Reggae"),
         ("Blues", "Blues"),
         ("Others", "Others"),
         ("Electronic", "Electronic"),
         
         
    )
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='album_covers/')
    song = models.ForeignKey(Post, related_name="albumsong", on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    genres = models.CharField(max_length=50,choices= Album_Genres_choices, default="Others")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        





    