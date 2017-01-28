from flask import Flask, render_template, request, redirect, url_for
from database import *
import flask_login, json, re
from bson.objectid import ObjectId
from jinja2 import evalcontextfilter, Markup, escape

app = Flask(__name__)
app.secret_key = '80e48d13643b4b2f53663be3967bcc76' #pharma-c
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class LoginUser(flask_login.UserMixin):
    role = None
    pass

@login_manager.user_loader
def user_loader(username):
    collection = database.users
    u = collection.User.find_one({'uid': str(username)})
    if u is None:
        return

    user = LoginUser()
    user.id = username
    user.role = u['role']
    return user

@login_manager.request_loader
def request_loader(req):
    username = req.form.get('username')
    password = req.form.get('password')

    collection = database.users
    u = collection.User.find_one({'uid': str(username)})
    if u is None:
        return

    user = LoginUser()
    user.id = username
    user.role = u['role']
    
    return user

@app.route("/")
def main_page():
    return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print username, password

    collection = database.users
    u = collection.User.find_one({'uid': str(username)})
    
    if (u is not None):
        if (password == u['password']):
            user = LoginUser()
            user.id = username
            user.role = u['role']
            flask_login.login_user(user)
            
            return redirect(url_for('dashboard'))

    return render_template('login.html', login_msg="Bad login. Try again!")

@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    if flask_login.current_user.role == 'teacher':
        return render_view()
    else:
        return render_annotate()

@app.route('/dashboard/upload')
@flask_login.login_required
def render_upload():
    return render_template('upload.html',
        username=flask_login.current_user.id,
        role=flask_login.current_user.role)

@app.route('/dashboard/view')
@flask_login.login_required
def render_view():
    collection = database.documents
    documents = collection.Document.find({'uid': flask_login.current_user.id})

    # print list(documents)

    return render_template('view.html',
        username=flask_login.current_user.id,
        role=flask_login.current_user.role,
        documents=documents)

# @app.route('/dashboard/<page>')
# @flask_login.login_required
# def render_page(page):
#     return render_template('main.html',
#         username=flask_login.current_user.id,
#         role=flask_login.current_user.role,
#         page=page)

@app.route("/save/document", methods=['POST'])
@flask_login.login_required
def add_document():
    if flask_login.current_user.role != "teacher":
        return unauthorized_handler()

    text = request.form['text']
    title = request.form['title']
    uid = flask_login.current_user.id

    collection = database.documents    
    p = collection.User.find_and_modify(
        query={"title": str(title), "uid": uid},
        update={"$set": {"title": str(title), "text": str(text), "uid": uid}
    }, new=True, upsert=True)

    return render_template('upload.html',
        username=flask_login.current_user.id,
        role=flask_login.current_user.role,
        text=text, title=title, upload=True)

@app.route("/edit/document/<did>")
@flask_login.login_required
def edit_document(did):
    if flask_login.current_user.role != "teacher":
        return unauthorized_handler()

    collection = database.documents    
    d = collection.Document.find_one(ObjectId(did))
    
    if(d):
        text = d['text']
        title = d['title']
        return render_template('upload.html',
            username=flask_login.current_user.id,
            role=flask_login.current_user.role,
            text=text, title=title)

@app.route("/delete/document/<did>")
@flask_login.login_required
def delete_document(did):
    if flask_login.current_user.role != "teacher":
        return unauthorized_handler()

    collection = database.documents    
    d = collection.Document.find_one(ObjectId(did))
    
    if(d):
        if(d['uid'] == flask_login.current_user.id):
            d.delete()
        
        documents = collection.Document.find({'uid': flask_login.current_user.id})

        return render_template('view.html',
            username=flask_login.current_user.id,
            role=flask_login.current_user.role,
            documents=documents,
            delete=True)

@app.route('/dashboard/annotate')
@flask_login.login_required
def render_annotate():
    collection = database.students
    teacher = collection.Document.find_one({'uid': flask_login.current_user.id})

    documents = None

    if (teacher):
        collection = database.documents
        documents = collection.Document.find({'uid': teacher['tid']})

        # print list(documents)

    return render_template('annotate.html',
        username=flask_login.current_user.id,
        role=flask_login.current_user.role,
        documents = documents)

def nl2br(text):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
    
    return u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(text)))

@app.route("/view/annotation/<did>")
@flask_login.login_required
def view_annotation(did):
    collection = database.documents    
    d = collection.Document.find_one(ObjectId(did))
    
    if(d):
        text = d['text']
        title = d['title']

        return render_template('annotator.html',
            username=flask_login.current_user.id,
            role=flask_login.current_user.role,
            text=nl2br(text), title=title, did=did)

@app.route("/create/annotations/<did>", methods=['POST'])
@flask_login.login_required
def create_annotations(did):
    collection = database.annotations
    record = {  "uid": flask_login.current_user.id,
                "did": did,
                "annotation": str(request.data),
                "connection": u"None"
             }

    p = collection.Annotation.find_and_modify(
        query=record, update={"$set": record}, new=True, upsert=True)

    j = json.loads(request.data)
    j["id"] = str(p["_id"])
    return json.dumps(j)

@app.route("/read/annotations/<did>", methods=['GET'])
@flask_login.login_required
def read_annotations(did):
    collection = database.annotations
    annotations = collection.Annotation.find({
        'uid': flask_login.current_user.id,
        'did': did
        })

    annotations = list(annotations)
    records = []
    for a in list(annotations):
        j = json.loads(a['annotation'])
        j['id'] = str(a['_id'])
        records.append(j)

    # records ={'rows': [{'category': 'evidence', 'linespan': 'Paragraph undefined', 'quote': u"of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content he", 'ranges': [{'start': '/div[1]/div[1]/div[1]/div[2]/p[5]', 'end': '/div[1]/div[1]/div[1]/div[2]/p[5]', 'startOffset': 87, 'endOffset': 263}], 'user': 'test', 'text': 'sdfsf trying again', 'data_creacio': 1478384325003, 'id': '581e5ac595b640bf07dbf987', 'permissions': {'read': ['test'], 'admin': ['test'], 'update': ['test'], 'delete': ['test']}}], 'total': 1}
    print records

    return json.dumps(records)

@app.route("/update/annotations/<aid>", methods=['PUT'])
@flask_login.login_required
def update_annotations(aid):
    collection = database.annotations
    a = collection.Annotation.find_one(ObjectId(str(aid)))
    print a['annotation']
    a['annotation'] = unicode(request.data, "utf-8")
    print a['annotation']
    a.save()

    return json.dumps({"id": aid})

@app.route("/destroy/annotations/<aid>", methods=['DELETE'])
@flask_login.login_required
def destroy_annotations(aid):
    collection = database.annotations
    a = collection.Annotation.find_one(ObjectId(str(aid)))

    if(a):
        a.delete()

    return ('', 204)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html', login_msg="Logged out!")

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', login_msg="Please login!")

#Admin functions
@app.route("/argupod-admin/create/user/<uid>/<password>/<role>")
def create_user(uid, password, role):
    collection = database.users
    
    p = collection.User.find_and_modify(
        query={"uid": str(uid)},
        update={"$set": {"uid": str(uid), "password": password, "role": role}
    }, new=True, upsert=True)
    
    p.pop("_id", None)
    return json.dumps(p)

@app.route("/argupod-admin/assign/teacher/<uid>/<tid>")
def create_student(uid, tid):
    collection = database.students
    
    p = collection.User.find_and_modify(
        query={"uid": str(uid)},
        update={"$set": {"uid": str(uid), "tid": str(tid)}
    }, new=True, upsert=True)
    
    p.pop("_id", None)
    return json.dumps(p)


# @app.route(SERVER_PATH + '/set/variable/<pid>/<session>/<var>/<value>/<var_type>')
# def save_session_var(pid, session, var, value, var_type):
#     p = collection.Variable.find_and_modify(
#         query={"pid": str(pid), "session": str(session), "variable": var},
#         update={"$set": {"value": value, "type": var_type, "time": time.time()}
#     }, new=True, upsert=True)
#     p.pop("_id", None)
#     return json.dumps(p)
    
if __name__ == "__main__":
    app.run(debug=True)
