from flask import (
	Flask, 
	render_template, 
	flash, 
	request, 
	redirect, 
	url_for,
	session,
        send_from_directory
)
from werkzeug import secure_filename
import os
import model
import tags
from pagination import Pagination

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER=os.environ['OPENSHIFT_DATA_DIR']
))
#app.config.from_envvar('FLASKR_SETTINGS', silent=False)
app.config.from_pyfile(os.environ['OPENSHIFT_REPO_DIR']+"/wsgi/config.txt")

@app.context_processor
def utility_processor():
    def format_tags(t):
        # Make the format tags method accessible in the views
        return tags.format_tags(t)
    return dict(format_tags=format_tags)

@app.context_processor
def inject_flags():
    # Make the tags accessible in the views
    return dict(tags=model.get_tags())

@app.route("/", defaults={'page':1})
@app.route("/page/<int:page>")
def index(page):
        # Return all articles and display them in the index template
        num_posts = model.count_articles() 
        pagination = Pagination(page, num_posts)
	articles = model.get_articles(page)
	return render_template('index.html', articles=articles, pagination=pagination)

@app.route("/list/<tag>", defaults={'page':1})
def list(tag, page):
        # List all articles for a given tag and display them
        num_posts = model.count_articles(tag)
        articles = model.get_articles(page, tag=tag)
        return render_template('list.html', articles=articles)

@app.route("/view/<id>")
def view_post(id):
        # Display a post from its id
	article = model.get_article(id)
	return render_template('view.html', article=article)

@app.route("/new", methods=['GET', 'POST'])
def new_post():
        # Create a new article
        # GET generates the form
        # POST creates it in DB
	if request.method=='GET':
		return render_template('new.html')
	elif request.method=='POST':
		model.new_post(request.form['title'], request.form['abstract'], request.form['text'],request.form['tags'])
	return redirect(url_for('index'))

@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit_post(id):
        # Edit an article
        # GET reloads the article from the DB and creates the form
        # POST edits in DB
	article = model.get_article(int(id))
	if request.method=='GET':
		return render_template('edit.html', article=article)
	elif request.method=='POST':
		model.edit_post(request.form['title'], request.form['abstract'], request.form['text'], request.form['tags'], article)
		return redirect(url_for('view_post', id=int(id)))

@app.route("/delete/<id>")
def delete_post(id):
        # Deletes an article given its id
	model.del_article(int(id))
	return redirect(url_for('index'))

@app.route("/login", methods=['GET', 'POST'])
def login():
        # Logs the user in
        # GET generates the form
        # POST validates the credentials against the configuration
	error = None
	if request.method=='GET':
		return render_template('login.html')
	elif request.method=='POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
			return render_template('login.html', error=error)
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
			return render_template('login.html', error=error)
		else:
			session['logged'] = True
			return redirect(url_for('index'))

@app.route("/logout")
def logout():
        # Logs the user out
	session['logged'] = False
	return redirect(url_for('index'))

@app.route("/upload", methods=['GET', 'POST'])
def upload():
        # Uploads a file to the upload folder
        # GET generates the form and file picker
        # POST uploads the file to the correct folder
        if request.method=='GET':
                return render_template('upload.html')
        elif request.method=='POST':
                file = request.files['file']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('index'))

@app.route("/publish/<id>")
def publish(id):
        # Publish an article, removing the 'draft' status
        article = model.get_article(id)
        if session['logged']:
                model.publish(article)
        return redirect(url_for('view_post', id=int(id)))

@app.route("/unpublish/<id>")
def unpublish(id):
        # Unpublish an article, setting the 'draft' status
        article = model.get_article(id)
        if session['logged']:
                model.unpublish(article)
        return redirect(url_for('view_post', id=int(id)))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Returns a file from the uploaded folder
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)     

if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
