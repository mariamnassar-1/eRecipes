# eRecipes

#### Introduction:
My CS50 final project is a web app that i made using Flask, Python, and SQL: eRecipes. It's a virtual cookbook that provides a platform for users to create and exchange their own recipes with each other.


#### Register, Log In, and Log Out
The registration feature enables users to create individual accounts that they can log back into whenever they want. The log-out option ensures the secure exit from your account.

#### Home
The "Home" page enables users to browse and discover recipes shared by other users. Each recipe is presented with essential details such as the creator's username, recipe name, image, ingredients, steps, and other additional information. By clicking on a username, users can explore the creator's cookbook, gaining access to all their posted recipes. A search bar located at the top left for easy retrieval of specific recipes by name.

#### My Cookbook
The "My Cookbook" feature provides a space to save your own recipes. This page displays all recipes you have added, mimicking the format of the home page except its only your own posts.

#### Add Recipe
The "Add Recipe" form is what allows users to contribute their creations to the web app. Upon clicking, users are directed to a page where they can submit a form containing key recipe details, including name, ingredients, steps, an image, and more. Upon submission, the recipe becomes accessible on both the home page and the "My Cookbook" page.

#### The Database: project.db
The database comprises four tables: "users," "recipes," "ingredients," and "steps." The "users" table stores user information upon registration(username, password, and user_id), while the "recipes" table holds most of the recipe data(id, user_id, name, image url, cook method, and meal type). The "ingredients" and "steps" tables, with foreign keys linking to the "recipes" table, store detailed information on ingredients (ingredients and amount per ingredient) and steps(steps in order).

#### helpers.py
The login_required function ensures that users are logged in before accessing any features. The apology function returns an apology picture (apology.html) in case of misuse by a user. The allowed_file function ensures that the image uploaded by the user has a correct extension for images (e.g., jpg, png).
#### layout.html
The layout template is my base for this app. It mainly includes the navbar as well as other functions that would be common in the other templates.

#### Conclusion
eRecipes caters to a specific audience, myself included. As someone who finds peace in baking as a favorite stress-relieving hobby, this app allows me to archive and revisit my favorite recipes at any time. While the appeal may not be universal, those who share this passion are likely to appreciate the unique value this platform offers.
