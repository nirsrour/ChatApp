from datetime import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from chat.models import UserSetting, Message, Chat


# homepage for anonymous clients and known clients
def anonymous_index(request):
    return render(request, "anonymous_index.html", {"username": None})


def index(request, pk):

    query = UserSetting.objects.filter(id=pk)

    if len(query) == 0:
        return redirect('/')

    return render(request, "index.html", {"username": query[0].username, "id": query[0].id})


# login
def login(request):
    return render(request, "login.html", {})


def login_user(request):
    if request.method == 'POST':
        form = request.POST
        username = form['username']
        input_password = form['password']

        if not check_user_exists_by_username(username):
            return redirect("/")

        query = list(UserSetting.objects.raw(
            "SELECT * FROM chat_usersetting WHERE username=%s", [username]))[0]
        passowrd = query.password
        if input_password == passowrd:
            id = str(query.id)

            return HttpResponseRedirect(reverse("home", args=(id,)))

    return redirect('/login')


# sign-up
def sign_up(request):
    return render(request, "sign_up.html", {})


def add_user(request):
    if request.method == 'POST':
        form = request.POST
        full_name = form['full_name']
        email = form['email']
        username = form['username']
        password = form['password']

        if check_user_exists_by_username(username):
            return redirect("/")

        obj = UserSetting(full_name=full_name, email=email,
                          username=username, password=password)
        obj.save()

        query = list(UserSetting.objects.raw(
            "SELECT * FROM chat_usersetting WHERE username=%s", [username]))

        id = str(query[0].id)
        username = query[0].username
        return HttpResponseRedirect(reverse("home", args=(id,)))

    return redirect("/sign_up")


# utils functions
def is_chat_exists(first_user, second_user):
    return Chat.objects.filter(first_user__username=first_user.username, second_user__username=second_user.username).exists()


def create_chat(first_user, second_user):
    chat = Chat(first_user=first_user, second_user=second_user,
                is_chat_active=True)
    chat.save()


def check_user_exists_by_username(username):
    return UserSetting.objects.filter(username=username).exists()


def check_user_exists_by_id(id):
    return UserSetting.objects.filter(id=id).exists()


def get_msgs(first_user, second_user):
    msgs1 = Message.objects.filter(sender=first_user, receiver=second_user)
    msgs2 = Message.objects.filter(sender=second_user, receiver=first_user)

    msgs = sorted([*msgs1, *msgs2],
                  key=lambda x: x.msg_time, reverse=False)

    return msgs


# add message to the DB
def add_msg_to_db(first_user, second_user, msg):
    obj = Message(sender=first_user, receiver=second_user, msg=msg)
    obj.save()


def add_msg(request):
    if request.method == 'POST':
        form = request.POST
        sender = form['sender']
        receiver = form['receiver']
        msg = form['msg']

        if not check_user_exists_by_username(sender) or not check_user_exists_by_username(receiver):
            id = UserSetting.objects.filter(username=sender)[0].id
            return render(request, "index.html", {"username": sender, "id": id})

        first_user = UserSetting.objects.filter(username=sender)[0]
        second_user = UserSetting.objects.filter(username=receiver)[0]

        if not is_chat_exists(first_user, second_user):
            create_chat(first_user, second_user)

        add_msg_to_db(first_user, second_user, msg)

        return render(request, "chat_msgs.html", {"first_user": first_user, "second_user": second_user, "msgs": get_msgs(first_user, second_user), "id": first_user.id})

    return redirect("/")


# display all chats for a given user
def chats(request, pk):
    user_query = UserSetting.objects.filter(id=pk)[0]
    if not check_user_exists_by_id(pk):
        return render(request, "index.html", {"username": user_query.username, "id": user_query.id})
        # return redirect("/")

    query1 = Chat.objects.filter(first_user=user_query)
    query2 = Chat.objects.filter(second_user=user_query)

    return render(request, "chats.html", {"chats": [*query1, *query2], "id": pk, "username": user_query.username})


# display all users in the system
def all_users(request, pk):
    user = UserSetting.objects.filter(id=pk)[0]
    users = UserSetting.objects.exclude(id=pk)
    return render(request, "all_users.html", {"users": users, "id": pk, "username": user.username})


# change chat status to active/not active
def change_status(request):
    if request.method == 'POST':
        form = request.POST
        fu_id = form['fu_uuid']
        su_id = form['su_uuid']
        username = form['username']

        chat_obj = Chat.objects.filter(
            first_user__id=fu_id, second_user__id=su_id)[0]

        flag = chat_obj.is_chat_active
        chat_obj.is_chat_active = not flag
        chat_obj.save()

        id = chat_obj.first_user.id if chat_obj.first_user.username == username else chat_obj.second_user.id

        user_query = UserSetting.objects.filter(id=id)[0]
        query1 = Chat.objects.filter(first_user=user_query)
        query2 = Chat.objects.filter(second_user=user_query)
        return render(request, "chats.html", {"chats": [*query1, *query2], "id": id, "username": username})

    redirect('/')


# display all messages between two given users
def chat_msgs(request):

    if request.method == 'POST':
        form = request.POST
        fu_username = form['fu_username']
        su_username = form['su_username']
        first_user = UserSetting.objects.filter(username=fu_username)[0]

        if not check_user_exists_by_username(su_username):
            return render(request, "index.html", {"username": fu_username, "id": first_user.id})

        second_user = UserSetting.objects.filter(username=su_username)[0]

        msgs = get_msgs(first_user, second_user)
        return render(request, "chat_msgs.html", {"first_user": first_user, "second_user":
                                                  second_user,
                                                  "msgs": msgs,
                                                  "id": first_user.id,
                                                  "username": fu_username})

    redirect("/")
