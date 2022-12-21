from botCounsellor import db,datetime,loginManager,UserMixin,mm

@loginManager.user_loader
def loader(id):
    admin = Admin.query.get(int(id))
    if admin:
        return admin
    else:
        return Users.query.get(int(id)) 


class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imageFile = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    userType = db.Column(db.String(10), nullable=False)
    messages = db.relationship('Messages',backref='sendBy',lazy=True)
    reviews = db.relationship('Reviews',backref='givenBy',lazy=True)
    blogs = db.relationship('Blogs',backref='author',lazy=True)
    comments = db.relationship('Comments',backref='postedBy',lazy=True)

class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(500),nullable=False)
    sender = db.Column(db.String(10),nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)    

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    datePosted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    imageFile = db.Column(db.String(100), nullable=False, default='defaultBlog.jpg')
    psychiatristsId = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)


class Reviews(db.Model):
    id = db.Column(db.Integer,  primary_key=True)
    datePosted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)

class Comments(db.Model):
    id = db.Column(db.Integer,  primary_key=True)
    datePosted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    blogId = db.Column(db.Integer,db.ForeignKey('blogs.id'), nullable=False)
    
class ReviewsSchema(mm.ModelSchema):
    class Meta:
        model = Reviews

class MessagesSchema(mm.ModelSchema):
    class Meta:
        model = Messages

class CommentsSchema(mm.ModelSchema):
    class Meta:
        model = Comments
