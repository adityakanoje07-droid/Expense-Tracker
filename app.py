from datetime import datetime

from flask import Flask, render_template, request, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.String(20), nullable=False)



@app.route("/")
@app.route("/home")
def home():

    expenses = Expense.query.all()

    total_expense = sum(exp.amount for exp in expenses)

    current_month = datetime.now().month

    monthly_expense = sum(
        exp.amount
        for exp in expenses
        if datetime.strptime(exp.date, "%Y-%m-%d").month == current_month
    )

    total_categories = len(set(exp.category for exp in expenses))

    return render_template(
        'home.html',
        total_expense=total_expense,
        monthly_expense=monthly_expense,
        total_categories=total_categories
    )


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():

    if request.method == 'POST':

        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        new_expense = Expense(
            amount=amount,
            category=category,
            description=description,
            date=date
        )

        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')

@app.route('/dashboard')
def dashboard():

    expenses = Expense.query.all()

    return render_template(
        'dashboard.html',
        expenses=expenses
    )

@app.route('/edit_expense/<int:id>',
           methods=['GET', 'POST'])
def edit_expense(id):

    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':

        expense.amount = request.form['amount']
        expense.category = request.form['category']
        expense.description = request.form['description']
        expense.date = request.form['date']

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template(
        'edit_expense.html',
        expense=expense
    )

@app.route('/delete_expense/<int:id>')
def delete_expense(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect(url_for('dashboard'))

# FIXED CODE:
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates your database tables safely
    app.run(debug=True)