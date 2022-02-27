from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.
from django.contrib import messages
from .forms import GroupCheckForm,PostForm
from .models import Group,Friend,Message
from django.core.paginator import Paginator
from django.db.models import Q


@login_required(login_url="/admin/login/")
def index(request,page=1):
	(public_user,public_group) = get_public()

	if request.method == "POST":
		checkform = GroupCheckForm(request.user,request.POST)
		glist = []
		for item in request.POST.getlist("groups"):
			glist.append(item)
		print(glist)
		messages = get_user_group_message(request.user,glist,page)
	else:
		checkform = GroupCheckForm(request.user)
		gps = Group.objects.filter(owner=request.user)
		print("gps: ",gps)
		glist = [public_group.title]
		print("glist: ",glist)
		for item in gps:
			glist.append(item.title)
		print("glist: ",glist)
		messages = get_user_group_message(request.user,glist,page)
		print("messages1: ",messages)
		params = {
			"login_user": request.user,
			"contents": messages,
			"check_form": checkform,
		}
		print("params: ",params)
		return render(request,"sns/index.html",params)



@login_required
def post(request):
	if request.method == "POST":
		gr_name = request.POST["groups"]
		print("gr_name: ",gr_name)
		content = request.POST["content"]
		print("content: ",content)
		group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
		print("group: ",group)

		if group == None:
			(pub_user,group) = get_public()
		msg = Message()
		print("msg: ",msg)
		msg.owner = request.user
		msg.group = group
		msg.content = content
		msg.save()
		messages.success(request,"new message sent")
		return redirect(to="/sns")

	else:
		form = PostForm(request.user)

	params = {
		"login_user": request.user,
		"form":form
	}
	return render(request,"sns/post.html",params)

@login_required(login_url="/admin/login/")
def share(request,share_id):
	share = Message.objects.get(id=share_id)
	print(share)
	if request.method == "POST":
		gr_name = request.POST["groups"]
		content = request.POST["content"]
		group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
		if group == None:
			(pub_user,group) = get_public()
		msg = Message()
		msg.owner = request.user
		msg.group = group
		msg.content = content
		msg.share_id = share.id
		msg.save()
		share_msg = msg.get_share()
		share_msg.share_count += 1
		share_msg.save()
		messages.success(request,"message is shared")
		return redirect(to="/sns")
	
	form = PostForm(request.user)
	params = {
		"login_user":request.user,
		"form":form,
		"share":share,
	}
	return render(request,"sns/share.html",params)

def get_user_group_message(owner,glist,page):
	page_num = 10
	(public_user,public_group) = get_public()
	groups = Group.objects.filter(Q(owner=owner)|Q(owner=public_user)).filter(title__in=glist)
	print("Groups: ",groups)
	me_friends = Friend.objects.filter(group__in=groups)
	print("me_friends: ",me_friends)
	me_users = []
	for f in me_friends:
		me_users.append(f.user)
	print("Me_users: ",me_users)

	his_groups = Group.objects.filter(owner__in=me_users)
	print("his_groups: ",his_groups)
	his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
	print("his_friends: ",his_friends)
	me_groups = []
	for hf in his_friends:
		me_groups.append(hf.group)
	print("me_groups: ",me_groups)
	messages = Message.objects.filter(Q(group__in=groups)|Q(group__in=me_groups))
	print("messages2: ",messages)
	page_item = Paginator(messages,page_num)
	print("what: ",page_item.get_page(page))
	return page_item.get_page(page)


def get_public():
	public_user = User.objects.filter(username="public").first()
	print("public_user: ",type(public_user),public_user)
	public_group = Group.objects.filter(owner = public_user).first()
	print("public_group: ",type(public_group),public_group)
	return (public_user,public_group)
