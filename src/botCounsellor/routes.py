from botCounsellor import app,db,render_template,url_for,flash,redirect,request,bcrypt,\
    login_user,current_user,logout_user,login_required,secrets,Image,abort,jsonify,os,fields,\
        fieldval,questions,questionIndex,np,sendSuggestion,starts
from botCounsellor.models import Blogs,Users,Admin,Reviews,ReviewsSchema,Messages,MessagesSchema,Comments,CommentsSchema
from botCounsellor.forms import registerForm,loginForm,blogForm
from botCounsellor.chatbot import chatbot_response


@app.route('/')
@app.route('/home')
def home():
    blogs = Blogs.query.all()
    admin = None
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('home.html',title='Home',blogs=blogs,admin=admin)


@app.route('/register',methods=['GET','POST'])
def register():
    userType = 'stu'
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(id=current_user.id).first()
        if admin:
            userType = 'psy'
        else:
            flash('user can not do change','danger')
            return redirect(url_for('home'))
    form = registerForm()
    if form.validate_on_submit():
        hashedPassword = bcrypt.generate_password_hash(form.password.data)
        user = Users(userName=form.userName.data,email=form.email.data,password=hashedPassword,userType=userType)
        db.session.add(user)
        db.session.commit()
        flash(f'account created by the name of {form.userName.data}','info')
        return redirect(url_for('home'))
    return render_template('register.html',title='Register',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        getUser = Users.query.filter_by(email=form.email.data).first()
        getAdmin = Admin.query.filter_by(email=form.email.data).first()
        if getAdmin and bcrypt.check_password_hash(getAdmin.password,form.password.data):
            flash('admin login','success')
            login_user(getAdmin)
        elif getUser and bcrypt.check_password_hash(getUser.password,form.password.data):
            login_user(getUser)
            flash('user login','success')
        else:
            flash('incorrect','danger')
            return redirect(url_for('login'))
        nextPage = request.args.get('next')
        return redirect(nextPage) if nextPage else redirect(url_for('home'))    
    return render_template('login.html',title='Login',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html',title='Account')

def saveImage(imageFile,dest):
    randomHax = secrets.token_hex(6)
    _,fileExtention = os.path.splitext(imageFile.filename)
    fileName = randomHax + fileExtention
    filePath =os.path.join(app.root_path, 'static',dest, fileName)

    outputSize = (500,500)
    i = Image.open(imageFile)
    i.thumbnail(outputSize)
    i.save(filePath)

    return filePath



@app.route('/addBlog', methods=['GET', 'POST'])
@login_required
def addBlog():
    form = blogForm()
    if form.validate_on_submit():
        if form.imageFile.data:
            image = saveImage(form.imageFile.data,'blogPictures')
            blog = Blogs(title=form.title.data,content=form.content.data,imageFile=image,psychiatristsId=current_user.id)
        blog = Blogs(title=form.title.data,content=form.content.data,psychiatristsId=current_user.id)
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('addBlog.html',form=form,toDo='Add Blog')

@app.route('/blog/<int:id>')
def blog(id):
    blog = Blogs.query.get_or_404(id)
    admin = None
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(id=current_user.id).first()
    title='Blog | ' + blog.title
    allComments = Comments.query.all()
    return render_template('blog.html',title=title,blog=blog,admin=admin,allComments=allComments)

@app.route('/blog/<int:id>/delete',methods=['POST'])
@login_required
def deleteBlog(id):
    blog = Blogs.query.get_or_404(id)
    admin = Admin.query.get(current_user.id)
    if blog.author == current_user or  admin:
        db.session.delete(blog)
        db.session.commit()
        flash('post deleted','info')
        return redirect(url_for('home'))
    abort(403)


@app.route('/blog/<int:id>/update',methods=['POST','GET'])
@login_required
def updateBlog(id):
    blog = Blogs.query.get_or_404(id)
    if blog.author != current_user:
        abort(403)
    form = blogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        if form.imageFile.data:
            image = saveImage(form.imageFile.data,'blogPictures')
            blog.imageFile = image
        db.session.commit()
        return redirect(url_for('blog',id=id))
    elif request.method == 'GET':
        form.title.data = blog.title
        form.content.data = blog.content
        form.imageFile.data = blog.imageFile
    return render_template('addBlog.html',title='Update Blog',form=form,toDo='Update Blog')


@app.route('/reviews')
def reviews():
    allReviews = Reviews.query.order_by(Reviews.datePosted)
    admin = None
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('reviews.html',title='Reviews',allReviews=allReviews,admin=admin)



@app.route('/deleteReview/<int:id>',methods=['POST'])
@login_required
def deleteReview(id):
    review = Reviews.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return None

@app.route('/deleteComment/<int:id>',methods=['POST'])
@login_required
def deleteComment(id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return None


@app.route('/addReview')
@login_required
def addReview():
    review = request.args.get('review')
    newReview = Reviews(content=review,userId=current_user.id)
    db.session.add(newReview)
    db.session.commit()
    reviewsSchema = ReviewsSchema()
    send = reviewsSchema.dump(newReview)
    return jsonify({'data':send})

@app.route('/addComment/<int:blogId>')
@login_required
def addComment(blogId):
    comment = request.args.get('comment')
    newComment = Comments(content=comment,userId=current_user.id,blogId=blogId)
    db.session.add(newComment)
    db.session.commit()
    commentSchema = CommentsSchema()
    send = commentSchema.dump(newComment)
    return jsonify({'data':send})

@app.route('/updateReview/<int:id>',methods=['GET'])
@login_required
def updateReview(id):
    review = Reviews.query.get_or_404(id)
    review.content = request.args.get('updatedRevew')
    db.session.commit()
    reviewsSchema = ReviewsSchema()
    send = reviewsSchema.dump(review)
    return jsonify({'data':send}) 

@app.route('/updateComment/<int:id>',methods=['GET'])
@login_required
def updateComment(id):
    comment = Comments.query.get_or_404(id)
    comment.content = request.args.get('updatedComment')
    db.session.commit()
    commentSchema = CommentsSchema()
    send = commentSchema.dump(comment)
    return jsonify({'data':send})


@app.route('/<string:userType>')
@login_required
def allUsers(userType):
    admin = Admin.query.get(current_user.id)
    if not admin:
        return abort(403)
    users = None
    active_item = None
    if userType == 'students':
        users = Users.query.filter_by(userType='stu').all()
        active_item = 'stu'
    elif userType == 'psychiatrists':
        users = Users.query.filter_by(userType='psy').all()
        active_item = 'psy'
    return render_template('users.html',users=users,admin=admin,active_item=active_item)

@app.route('/chatRoom/<int:id>')
@login_required
def chatRoom(id): 
    messages = Messages.query.filter_by(userId=id)
    return render_template('chatRoom.html',messages=messages)


@app.route('/chat')
@login_required
def chat():
    global questionIndex,fieldval
    responce = None
    message = request.args.get('message')
    msgSchma = MessagesSchema()
    msg = Messages(msg=message,sender='user',userId=current_user.id)
    db.session.add(msg)
    if message not in starts:
        responce = chatbot_response(message)
    if message in starts or responce in fields or responce == 'nothing':
        questionIndex += 1
        if questionIndex == 18:
            suggested_field = fields[np.argmax(fieldval)]
            if suggested_field == 'engineering':
                if fieldval[fields.index('computer scinece')] >4:
                    suggested_field = 'computer science'
            fieldval = [0 for _ in range(len(fields))]
            questionIndex = -1
            msg2 = Messages(msg=sendSuggestion(suggested_field),sender='bot',userId=current_user.id)
        else:
            try:
                fieldval[fieldval.index(responce)] += 1
            except:
                pass
            msg2 = Messages(msg=questions[questionIndex],sender='bot',userId=current_user.id)
    else:
        msg2 = Messages(msg=responce,sender='bot',userId=current_user.id)
    # if responce == 'I didn\'t understand. Please ask something else':
    #     msg2 = Messages(msg='I didn\'t understand. Please ask something else',sender='bot',userId=current_user.id)
    # elif responce not in fields:
    #     # if responce == 'okay then, i will ask you several questions. answer the desired one. so the questions are followed':
    #     #     mssg = Messages(msg='okay then, i will ask you several questions. answer the desired one. so the questions are followed',sender='bot',userId=current_user.id)
    #     #     db.session.add(mssg)
    db.session.add(msg2)
    db.session.commit()
    send = msgSchma.dump(msg2)
    return jsonify({'data':send})
    
@app.route('/showStudents')
@login_required
def showStudents():
    admin = None
    active_item = 'stu'
    users = Users.query.filter_by(userType='stu').all()
    return render_template('users.html',users=users,admin=admin,active_item=active_item)

@app.route('/deleteUser/<int:id>',methods=['POST'])
@login_required
def deleteUser(id):
    admin = Admin.query.filter_by(id=current_user.id).first()
    if not admin:
        abort(403)
    message = Messages.query.filter_by(userId=id).all()
    for i in message:
        db.session.delete(i)
    blog = Blogs.query.filter_by(psychiatristsId=id).all()
    for i in blog:
        db.session.delete(i)
    review = Reviews.query.filter_by(userId=id).all()
    for i in review:
        db.session.delete(i)
    comment = Comments.query.filter_by(userId=id).all()
    for i in comment:
        db.session.delete(i)
    user = Users.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))