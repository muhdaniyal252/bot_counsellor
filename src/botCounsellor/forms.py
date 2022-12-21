from botCounsellor import FlaskForm,StringField,PasswordField,SubmitField,BooleanField,TextAreaField,\
    DataRequired,Email,EqualTo,Length,ValidationError,FileField,FileAllowed
from botCounsellor.models import Users


class registerForm(FlaskForm):
    userName = StringField('User Name', validators=[DataRequired(),Length(min=3,max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
        getEmail = Users.query.filter_by(email=email.data).first()
        if getEmail:
            raise ValidationError('email already exists')

class loginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class blogForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(max=100)])
    content = TextAreaField('Content',validators=[DataRequired()])
    imageFile = FileField('Upload Image',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Post')

