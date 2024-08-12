import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os 
import urllib.request

from helpers import login_required, apology, allowed_file

# initialize app
app = Flask(__name__)

# for image upload
UPLOAD_FOLDER = "static/uploads/"

app.secret_key = "masdfnjdfn"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# configure server-side session management 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    #cache control for security (ex: if press back button after log out, no cache)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    

# only show search bar for some templates
showsearch = False


# display all recipes
@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    #open sqlite3 connection
    connection = sqlite3.connect('project.db', check_same_thread=False)
    db = connection.cursor()
    db.row_factory = sqlite3.Row
    
    # get recipes
    recipes = db.execute("SELECT * FROM recipes").fetchall()
    
    recipe_list = []

    for recipe in recipes:
        recipe_id = recipe["id"]
        
        # get username for each recipe
        result = db.execute("SELECT username FROM users WHERE id = ?", (recipe["user_id"], )).fetchone()
        username = result[0] if result else None
        
        # get ingredients and steps for each recipe
        ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id, )).fetchall()
        steps = db.execute("SELECT * FROM steps WHERE recipe_id = ?", (recipe_id, )).fetchall()
        
        # add all recipe details in a dictionary
        recipe_dict = {
        "username": username,
        "id": recipe_id,
        "name": recipe["name"],
        "type": recipe["type"],
        "cook": recipe["cook"],
        "image": recipe["image"],
        "ingredients": ingredients,
        "steps": steps
        }
        
        # save all recipes in a list of recipe_dicts
        recipe_list.append(recipe_dict)
    
    # save SQL commands
    connection.commit()
    connection.close()
        
    return render_template("index.html", recipe_list=recipe_list, show_search=True)

# other users' cookbook
@app.route("/usercookbook")
@login_required
def usercookbook():
    #open sqlite3 connection
    connection = sqlite3.connect('project.db', check_same_thread=False)
    db = connection.cursor()
    db.row_factory = sqlite3.Row
    
    # get recipes made by this user
    username = request.args.get('username')
    
    user_id_row = db.execute("SELECT id FROM users WHERE username = ?", (username, )).fetchone()   
    user_id = user_id_row["id"]
    
    recipes = db.execute("SELECT * FROM recipes WHERE user_id = ?", (user_id, )).fetchall()
    
    recipe_list = []

    for recipe in recipes:
        recipe_id = recipe["id"]
        
        # get ingredients and steps for each recipe
        ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id, )).fetchall()
        steps = db.execute("SELECT * FROM steps WHERE recipe_id = ?", (recipe_id, )).fetchall()
        
        # add all recipe details in a dictionary
        recipe_dict = {
        "id": recipe_id,
        "name": recipe["name"],
        "type": recipe["type"],
        "cook": recipe["cook"],
        "image": recipe["image"],
        "ingredients": ingredients,
        "steps": steps
        }
        # save all recipes in a list of recipe_dicts
        recipe_list.append(recipe_dict)
    
    # save SQL commands
    connection.commit()
    connection.close()

    return render_template("usercookbook.html", recipe_list=recipe_list, username=username, show_search=False)


# add a recipe
@app.route("/addrecipe", methods=["GET", "POST"])
@login_required
def addrecipe():
    if request.method == "POST":
        #open sqlite3 connection
        connection = sqlite3.connect('project.db', check_same_thread=False)
        db = connection.cursor()
        db.row_factory = sqlite3.Row
        
        # get recipe data from forms
        name = request.form.get("name")
        meal_type = request.form.get("meal_type")
        cook = request.form.get("cook")
        steps = request.form.getlist("steps[]")
        ingredients = request.form.getlist("ingredients[]")
        amounts = request.form.getlist("amounts[]")
        
        # get image
        if 'file' not in request.files:
            return apology("No file uploaded")
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))    
        else:
            return apology("Allowed image types: png. jpg, jpeg")
        
        image_url = url_for("static", filename="uploads/" + filename)
        
        # validate input
        if not name:
            return apology("Please enter recipe name")
        if not meal_type:
            return apology("Please enter meal type")
        if not cook:
            return apology("Please enter cooking method")
        if not ingredients:
            return apology("Please enter at least one ingredient")
        if not steps:
            return apology("Please enter at least one step")
        if not image_url:
           return apology("Please uploaad an image")
        
        # update recipes data base
        db.execute("INSERT INTO recipes (user_id, name, type, cook, image) VALUES(?, ?, ?, ?, ?)",
                   (session["user_id"], name, meal_type, cook, image_url))
        
        #recipe_id = db.execute("SELECT id FROM recipes WHERE user_id = ? AND name = ?", (session["user_id"], name))
        
        result = db.execute("SELECT id FROM recipes WHERE user_id = ? AND name = ?", (session["user_id"], name)).fetchone()
        recipe_id = result[0] if result else None
        
        # update ingredients data base
        for ingredient, amount in zip(ingredients, amounts):
            db.execute("INSERT INTO ingredients (recipe_id, name, amount) VALUES (?, ?, ?)",
                       (recipe_id, ingredient, amount))
        
        #update steps data base
        for step in steps:
            db.execute("INSERT INTO steps (recipe_id, step) VALUES (?, ?)", (recipe_id, step))
        
        # save SQL commands
        connection.commit()
        connection.close()
        
        # flash success message
        flash("Recipe added successfullly to your cookbook!")
        return redirect("/")
    
    # if method == GET
    else:
        return render_template("addrecipe.html", show_search=False)


# my cookbook
@app.route("/cookbook")
@login_required
def mycookbook():
    #open sqlite3 connection
    connection = sqlite3.connect('project.db', check_same_thread=False)
    db = connection.cursor()
    db.row_factory = sqlite3.Row
    
    # get recipes made by this user
    recipes = db.execute("SELECT * FROM recipes WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    recipe_list = []

    for recipe in recipes:
        recipe_id = recipe["id"]
        
        # get ingredients and steps for each recipe
        ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id, )).fetchall()
        steps = db.execute("SELECT * FROM steps WHERE recipe_id = ?", (recipe_id, )).fetchall()
        
        # add all recipe details in a dictionary
        recipe_dict = {
        "id": recipe_id,
        "name": recipe["name"],
        "type": recipe["type"],
        "cook": recipe["cook"],
        "image": recipe["image"],
        "ingredients": ingredients,
        "steps": steps
        }
        # save all recipes in a list of recipe_dicts
        recipe_list.append(recipe_dict)
    
    # save SQL commands
    connection.commit()
    connection.close()

    return render_template("cookbook.html", recipe_list=recipe_list, show_search=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    
    if request.method == "POST":
        # Ensure username and password are submitted
        if not request.form.get("username"):
            return apology("Please enter a username.", 403)
        elif not request.form.get("password"):
            return apology("Please enter a password.", 403)

        #open sqlite3 connection
        connection = sqlite3.connect('project.db', check_same_thread=False)
        db = connection.cursor()
        db.row_factory = sqlite3.Row
        
        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        
        # Ensure username exists
        rows = db.fetchall()
        if not rows:
            return apology("invalid username and/or password", 403)
        
        #Ensure password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # save SQL commands
        connection.commit()
        connection.close()

        # Redirect user to home page
        return redirect("/")

    # if method = GET
    else:
        return render_template("login.html")


# search for a recipe
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    recipe_list = []
    if request.method == "POST":
        #open sqlite3 connection
        connection = sqlite3.connect('project.db', check_same_thread=False)
        db = connection.cursor()
        db.row_factory = sqlite3.Row
    
        name = request.form.get("recipe_name")
        
        # if name is entered
        if name:
            search = db.execute("SELECT * FROM recipes WHERE name LIKE ?", ('%' + name + '%',)).fetchall()
            
            # if recipe is found
            if search:
                recipes = search
            else:
                return apology("recipe not found")
            
            for recipe in recipes:
                recipe_id = recipe["id"]
            
                # get username for each recipe
                result = db.execute("SELECT username FROM users WHERE id = ?", (recipe["user_id"], )).fetchone()
                username = result[0] if result else None
                
                # get ingredients and steps for each recipe
                ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id, )).fetchall()
                steps = db.execute("SELECT * FROM steps WHERE recipe_id = ?", (recipe_id, )).fetchall()
                
                # add all recipe details in a dictionary
                recipe_dict = {
                "username": username,
                "id": recipe_id,
                "name": recipe["name"],
                "type": recipe["type"],
                "cook": recipe["cook"],
                "image": recipe["image"],
                "ingredients": ingredients,
                "steps": steps
                }
                
                # save all recipes in a list of recipe_dicts
                recipe_list.append(recipe_dict)

            
             # Debugging statement to print recipe_list
            print("Recipe List:", recipe_list)
            # save SQL commands
            connection.commit()
            connection.close()
        
        else:
            return apology("please enter a recipe name to search")
        
        
        return render_template("index.html", recipe_list=recipe_list, show_search=True)
    else:
        return render_template("search.html", recipe_list=recipe_list, show_search=True)


@app.route("/logout")
def logout():
    # Forget user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username, password, and confirmation are submitted
        if not request.form.get("username"):
            return apology("Please enter a username.", 403)
        elif not request.form.get("password"):
            return apology("Please enter a password.", 403)
        elif not request.form.get("confirmation"):
            return apology("Please confirm your password.")

        # make sure password = confirmation
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Your passwords do not match.")
        
        #open sqlite3 connection
        connection = sqlite3.connect('project.db', check_same_thread=False)
        db = connection.cursor()
        db.row_factory = sqlite3.Row
        
        # Query database for usernam
        db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

        # Ensure username does not exist
        row = db.fetchone()
        if row is not None:
            return apology("this username already exists", 400)

        # add new user to database
        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (request.form.get("username"), hash))

        # query database for new user
        db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = db.fetchall()

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # save SQL commands
        connection.commit()
        connection.close()

        # Redirect user to home page
        return redirect("/")

    # if method = GET
    else:
        return render_template("register.html")

