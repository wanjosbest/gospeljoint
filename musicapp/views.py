import hashlib
from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from .models import (User,Post,Comment,Category, replycomment,promotedsongs,popularpost,newsletter,SongDownload,SongPlay,
                     songlike, trendingsongs,Playlist,Artist,PlaylistSong)
from .forms import (PasswordResetRequestForm, CustomSetPasswordForm,PasswordChangeForm, PlaylistForm)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes,force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse, FileResponse, Http404
from django.conf import settings
import os
from .models import (PremiumUser, Album,Userbrandedimage) # premium models

FRAME_PATH = "media/images/wanjos.jpg"

def index(request):
    #display ten recent post
    recentposts = Post.objects.all().order_by("-published")[:6]
    #trending songs
    trending = trendingsongs.objects.all().order_by("-date_added")[:6]
    # display five promoted songs
    promotedsongsdisplay = promotedsongs.objects.all().order_by("-date_added")[:6]
     # display five popular songs
    popularsongsdisplay = popularpost.objects.all().order_by("-date_added")[:6]
    context ={"recentposts":recentposts, "promotedsongs":promotedsongsdisplay,"popularsongsdisplay":popularsongsdisplay,
              "trending":trending
    }
    return render(request, "index.html", context)


def register_view(request):
    referal_username = request.GET.get("ref") # getting username from
    # Check if the HTTP request method is POST (form submission)
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        address = request.POST.get('address')
        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)
        
        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        # Create a new User object with the provided information
        referal_link = f"http://127.0.0.1:8000/{username}"
        user = User.objects.create(
            first_name=firstname,
            last_name=lastname,
            username=username,
            email = email,
            address = address,
            referal_link =  referal_link,
          
        )
        #encript password
        user.set_password(password)
        if referal_username:
            try:
                referer = User.objects.get(username= referal_username)
                user.reffered_by = referer
            except User.DoesNotExist:
                messages.error(request, "Invalid Referal Link")
        
        #save user
        user.save()
        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return redirect('/login/')
    
    # Render the registration page template (GET request)
    return render(request, 'user/register.html', {"referal_username": referal_username})

# logiin user
def login_view(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('login')
        user = authenticate(username=username, password=password) 
        
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('login')
            
        else:
            login(request,user)
            return redirect("index")
    return render(request, 'user/login.html')
# logout user

def logout_view(request):
    logout(request)
    return redirect('/login/')

#fogort password
@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if not check_password(old_password, user.password):
            messages.error(request, "Old password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        elif len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect('profile')
    return render(request, 'user/changepassword.html')



# Password reset request view
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    subject = "Password Reset Requested"
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    domain = get_current_site(request).domain
                    reset_link = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
                    reset_url = f'https://{domain}{reset_link}'
                    message = f"Click the link below to reset your password: {reset_url}"
                    send_mail(subject, message, 'josephwandiyahyel3@gmail.com', [email])
                return redirect("password_reset_done")
            else:
                return HttpResponse("Please you are not our User")
    else:
        form = PasswordResetRequestForm()
    return render(request, "user/password_reset_request.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(get_user_model(), pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = CustomSetPasswordForm(user)
        return render(request, "user/password_reset_confirm.html", {"form": form})
    else:
        return render(request, "user/password_reset_invalid.html")
    
def password_reset_complete(request):
    return render(request, "user/password_reset_complete.html") 

def password_reset_done(request):
    return render(request, "user/password_reset_done.html")  

#get post by user

def userposts(request):
    user = request.user
    userpost = Post.onjects.filter(user=user)
    context = {"userpost":userpost}
    return render (request, "user/posts.html",context)

#get post by category

def postbycategory(request, category ):
    
    categoryposts = Post.objects.filter(categories = category)
    context ={"categoryposts":categoryposts}
    return render(request, "categorypost.html", context)
#get all posts

def allposts(request):
    allpost = Post.objects.all()
    paginator = Paginator(allpost, 10) #number of songs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context ={"allpost":page_obj}
    return render(request, "allposts.html",context)
# get post details
def postdetails(request, slug):
    postde = Post.objects.get(slug = slug)
    postdetail = Post.objects.filter(slug = slug)
    pastecomments = Comment.objects.filter(post =postde).order_by("-date_added")[:10]
    related_songs = Post.objects.filter(genres = postde.genres).exclude(id = postde.id)[:5]
 
    
    #song play stats
    song = get_object_or_404(Post, slug = slug)
    song.play_count += 1
    song.save(update_fields = ["play_count"])
    context = {"postdetail":postde,"pastecomments":pastecomments,"related_songs":related_songs,"song":song}
     # collect and store comments on each post
    if request.method =="POST":
        post_id = request.POST.get("post_id") #get the post id
        name = request.POST.get("name")
        comment = request.POST.get("comment")
        savecomment = Comment.objects.create(post_id =post_id, name = name, content = comment)
        savecomment.save()
        messages.info(request, "Comment added Successfully")
    
    return render(request, "postdetails.html", context)


# save reply comment

def savereply(request,pk):
    commentid = Comment.objects.get(pk = pk)
    getcommentreply = replycomment.objects.filter(comment =commentid) .order_by("-date_added") 
    if request.method =="POST":
       comment_id = request.POST.get("commentid") #get the comment id
       name = request.POST.get("name")
       email = request.POST.get("email")
       comment = request.POST.get("comment")
       savereplycomment = replycomment.objects.create(comment_id = comment_id, name = name, email = email,content = comment)
       savereplycomment.save()
       messages.info(request, " Replied Successfully")
    context = {"getcommentreply":getcommentreply} 
    return render(request, "postdetails.html", context)

# search posts, user, artist, description and category
def search(request):
    if request.method == "POST":
        searched = request.POST.get("searched")
        searched = Post.objects.filter(title__icontains = searched)
        return render(request, "search.html",{"searched":searched})
    else:
        return render(request, "search.html")

#new letter subscriptions

def newsletterView(request):
    if request.method =="POST":
        email = request.POST.get("email")
        saveemail = newsletter.objects.create(email=email)
        saveemail.save()
        messages.info(request, "succesfullt subscribed to newsletter")
        subject = "Simnawa King News Letter Subscription"
        message = f" {email} Thanks for Subscribing to our Newsletter \n Just stay calmed and wait on our daily Music releases."
        send_mail(subject, message, "josephwandiyahyel3@gmail.com", [email])
    return render(request, "newsletter.html")

#send songs updates to newsletter subscribers

def sendmailtosubscribers(request):
    
    return ""

#allow musician to upload their songs
@login_required
def musicianuploadsong(request):
    user = request.user
    ref = User.objects.get(username = user)
    referer = ref.reffered_by #GET REFERAL USERNAME
    referal_bonus = 500  
    if request.method == "POST":
       title = request.POST.get("title")  
       body = request.POST.get("body")
       image = request.FILES.get("image")
       song = request.FILES.get("song")
       meta_keywords = request.POST.get("meta_keywords")
       meta_description = request.POST.get("meta_description")
       genres = request.POST.get("genres")
       slug = slugify(title)
       
       # add payment gateway here before uploading the song
       try:
          artisttitle = Post.objects.filter(user = request.user)
       except Post.DoesNotExist:
          artisttitle = None
       if song :
           hasher = hashlib.md5()
           for chunk in song.chunks():
               hasher.update(chunk)
               file_hash = hasher.hexdigest()
                #check for duplicate
               if Post.objects.filter(file_hash = file_hash).exists():
                  messages.error(request, "This Song already Exist")
                  return redirect("musicianuploadsong")
       if image :
           hasher = hashlib.md5()
           for chunk in image.chunks():
               hasher.update(chunk)
               image_hash = hasher.hexdigest()
                #check for duplicate
               if Post.objects.filter(image_hash = image_hash).exists():
                  messages.error(request, "This Image already Exist")
                  return redirect("musicianuploadsong")
       savesong = Post.objects.create(user=user,title=title,body=body,image=image, upload_song=song,meta_keywords=meta_keywords, meta_description = meta_description,genres=genres,slug=slug, file_hash = file_hash, image_hash= image_hash)
       savesong.save()
    #    referer.referal_wallet += referal_bonus #adding 500 naira to referer
    #    referer.save()  # save the bonus to the referer
       messages.success(request,"Song uploaded Successfully")
    return render(request, "user/uploadsong.html")
    # play count
# def songplay_count(request, song_id):
#     song = get_object_or_404(Post, id = song_id)
#     song.play_count += 1
#     song.save(update_fields = ["play_count"])
#     context = {"song":song}
#     return render(request, "postdetails.html", context)

# artist song lists
@login_required
def all_artist_songs(request):
    get_all_artist_songs = Post.objects.filter(user = request.user)
    context = {"all_songs":get_all_artist_songs}
    
    return render(request, "user/allartist_songs.html", context)
def increement_download_count(request, song_id):
    song = get_object_or_404(Post, id = song_id)
    song.download_count += 1
    song.save()
    return JsonResponse({"success":True,"download_count":song.download_count})
def download_song(request, song_id):
    song = get_object_or_404(Post, id = song_id)
    file_path = os.path.join(settings.MEDIA_ROOT, song.upload_song.NAME)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb', as_attachment=True))
    else:
        raise Http404("File Not Found")
    
#list of user uploaded songs
def songs(request, username):
    user = User.objects.get(username=username)
    getallsongs = Post .objects.filter(user= user)
    context ={"getallsongs": getallsongs }
    return render(request, "user/songs.html", context)



@login_required( redirect_field_name="next")
def artistprofile(request):
    getuserdetails = User.objects.get(username = request.user)
    get_userplaylist = Playlist.objects.filter(user = request.user)
    getusersongs = Post.objects.filter(user = request.user)[:10]

    # referal_link = get_refferal_link()
    context ={"userdetails":getuserdetails, "get_userplaylist":get_userplaylist,"getusersongs":getusersongs}

    return render(request, "user/profile.html", context)
@login_required()
def create_playlist(request):
    if request.method == "POST":
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, "Playlist created successfully!")
            return redirect('profile')
    else:
        form = PlaylistForm()
    return render(request, 'user/createplaylist.html', {'form': form})
@login_required
def addsongtoplaylist(request, song_id):
    if request.method == "POST":
        song = get_object_or_404(Post, id = song_id)
        playlists_id = request.POST.get("playlist_id")
        playlist = get_object_or_404(Playlist, id= playlists_id)
        user = request.user
        if song_id in user.playlists.all():
            messages.warning(request, "song already added")
        else:
            savesong = PlaylistSong(user = user, songs_id = song_id, playlist_id = playlists_id)
            savesong.save()
            return redirect("post_details", song.slug)
    return render(request, "postdetails.html")
    


@login_required()
def playlist_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'user/playlistlist.html', {'playlists': playlists})

@login_required()
def playlist_detail(request, playlist_id):
    playlist = Playlist.objects.get(id = playlist_id)
    return render(request, 'user/playlistdetails.html', {'playlist': playlist})
     
@login_required()
def editprofile(request):
    getuserfirst = request.user
    try:
        address = User.objects.get(username = getuserfirst)
    except User.DoesNotExist:
        address = None
    if request.method == "POST":
        address.image = request.FILES.get("profile")
        address.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect("profile")
    context = {"getuser":getuserfirst,"address":address}
    return render(request, "user/editprofile.html",context)

@login_required()
def editcoverimage(request):
    getuserfirst = request.user
    try:
        address = User.objects.get(username = getuserfirst)
    except User.DoesNotExist:
        address = None
    if request.method == "POST":
        address.cover_image = request.FILES.get("coverimage")
        address.save()
        messages.success(request, "Cover Image Updated Successfully")
        return redirect("profile")
    context = {"getuser":getuserfirst,"address":address}
    return render(request, "user/editcoverimage.html",context)

# upgrade to premium user
@login_required
def upgradetopremium(request):
    
    if request.method == "POST":
        #check if the user has premiun entry
        premium_exists = PremiumUser.objects.filter(user = request.user).exists()
        if premium_exists:
            messages.info(request, " you are already a premium User")
        else:
            another = PremiumUser.objects.create(user = request.user, is_premium = True)
            another.save()
            messages.success(request, "Upgraded to premium Successfully")
            return redirect("profile")
    return HttpResponse("Upgraded")

@login_required
def create_album(request):
    profile = request.user.premiumuser

    if not profile.is_premium:
        return render(request, 'user/upgrade_to_premium.html')

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        price = request.POST['price']
        cover = request.FILES['image']
        genres = request.POST["genres"]

        album = Album.objects.create(
            artist=request.user,
            title=title,
            description=description,
            price=price,
            cover=cover,
            genres = genres
        )
        return redirect('profile')

    return render(request, 'user/premium/create_album.html')

########################################################### Static Pages ############################################
# Contact us 

def contact_us(request):
    if request.method =="POST":
        subject = request.POST.get("subject")
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        send_mail(subject, message, "{email}",["josephwandiyahyel3@gmail.com"])
        messages.info(request, f"Thank you {name} for contacting Gospel Joint! Be calmed as Our agents will reply you to the email you've provided.")
    return render(request, "staticpages/contactus.html")  
def about_us(request): 
    return render(request, "staticpages/aboutus.html")  
def termconditions(request):
    return render(request, "staticpages/terms.html")  
def privacy(request): 
    return render(request, "staticpages/privacy.html")
def disclaimer(request): 
    return render(request, "staticpages/disclaimer.html")    
########################################################### Static Pages end ############################################
from PIL import Image
from django.core.files.storage import default_storage
@login_required
def branded_dp_generator(request):
    user = request.user
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            user_photo = request.FILES['photo']

            # Define the uploads directory inside MEDIA_ROOT
            upload_dir = 'uploads/'

            # Ensure the 'uploads/' directory exists
            upload_dir_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
            os.makedirs(upload_dir_path, exist_ok=True)

            # Save the uploaded photo
            photo_filename = user_photo.name
            photo_path = os.path.join(upload_dir_path, photo_filename)

            with open(photo_path, 'wb') as f:
                for chunk in user_photo.chunks():
                    f.write(chunk)

            # Open the uploaded photo
            uploaded_img = Image.open(photo_path)
            if uploaded_img.mode != "RGBA":
                uploaded_img = uploaded_img.convert("RGBA")

            # Open the frame image
            frame_path = os.path.join(settings.BASE_DIR, 'static', 'frames', 'gospel-removebg-preview.png')
            frame = Image.open(frame_path)
            if frame.mode != "RGBA":
                frame = frame.convert("RGBA")

            # Resize the frame to match the uploaded photo
            frame = frame.resize(uploaded_img.size)

            # Merge the uploaded photo and frame
            combined = Image.alpha_composite(uploaded_img, frame)

            # Save the combined image
            combined_filename = 'branded_' + photo_filename
            combined_path = os.path.join(upload_dir_path, combined_filename)
            combined.save(combined_path, format='PNG')  # Save as PNG to preserve transparency

            # Save the branded image URL (relative to media root) to the database
            branded_image_url = os.path.join(upload_dir, combined_filename)
            Userbrandedimage.objects.create(user=user, branded_image_url=branded_image_url)

            # URL for user to download/view
            branded_url = os.path.join(settings.MEDIA_URL, upload_dir, combined_filename)

            return render(request, 'user/branded_image_success.html', {'branded_url': branded_url})

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'user/branded_image.html')
