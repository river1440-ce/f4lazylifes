from datetime import datetime, timezone
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    session,
)
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, IndexAnonyServiceForm
from app.models import User
from app.main import bp
from app.main.helper import index_demo_data
import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# @bp.route('/set_email', methods=['GET', 'POST'])
# def set_email():
#     if request.method == 'POST':
#         # Save the form data to the session object
#         session['email'] = request.form['email_address']
#         return redirect(url_for('main.get_email'))

#     return """
#         <form method="post">
#             <label for="email">Enter your email address:</label>
#             <input type="email" id="email" name="email_address" required />
#             <button type="submit">Submit</button>
#         </form>
#         """
# @bp.route('/get_email')
# def get_email():
#     return render_template_string("""
#             {% if session['email'] %}
#                 <h1>Welcome {{ session['email'] }}!</h1>
#                 <p>
#                     <a href="{{ url_for('main.delete_email') }}">
#                         <button type="submit">Delete Email</button>
#                     </a>
#                 </p>
#             {% else %}
#                 <h1>Welcome! Please enter your email <a href="{{ url_for('main.set_email') }}">here.</a></h1>
#             {% endif %}
#         """)

# @bp.route('/delete_email')
# def delete_email():
#     # Clear the email stored in the session object
#     session.pop('email', default=None)
#     flash("Session deleted!")
#     return redirect(url_for('main.set_email'))


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    else:
        form = IndexAnonyServiceForm()
        if form.validate_on_submit():
            # breakpoint()
            start_year = form.start_year.data
            expense_amount = form.expense_amount.data
            investment_amount = form.investment_amount.data
            salary_amount = form.salary_amount.data
            house_start_year = form.house_start_year.data
            house_amount = form.house_amount.data
            down_payment = form.down_payment.data
            interest = form.interest.data
            loan_term = form.loan_term.data
            child_born_at_age = form.child_born_at_age.data
            investment_ratio = form.investment_ratio.data
            retire_age = form.retire_age.data

            monthly_house_debt = (
                (house_amount - down_payment) * (1 + interest * 0.01)
            ) / (loan_term * 12)

            x = np.arange(start_year, 86, dtype=int)
            y = np.empty(x.size)
            for this_year in x:
                if this_year >= retire_age:
                    salary_amount = 0

                left = salary_amount - expense_amount

                pay_houst_debt = (this_year >= house_start_year) & (
                    this_year < house_start_year + loan_term
                )
                if pay_houst_debt:
                    left = left - monthly_house_debt

                raise_child = (this_year >= child_born_at_age) & (
                    this_year < child_born_at_age + 22
                )
                if raise_child:
                    left = left - 15000

                saving = left * investment_ratio * 0.01

                # Update
                investment_amount = investment_amount * 1.05 + saving
                y[this_year - start_year] = investment_amount

                salary_amount = salary_amount * 1.01
                expense_amount = expense_amount * 1.01
            # Generate the figure **without using pyplot**.
            fig = Figure()
            ax = fig.subplots()
            ax.plot(x, y)
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            data = base64.b64encode(buf.getbuffer()).decode("ascii")

            session["data"] = data
            return redirect(url_for("main.index"))

        if "data" not in session:
            data = index_demo_data
        else:
            data = session["data"]
            session.pop("data", default=None)
        return render_template("index.html", form=form, data=data)


@bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


@bp.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template("user.html", user=user)


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("變更已儲存！")
        return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)
