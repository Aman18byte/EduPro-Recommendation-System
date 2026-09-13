import streamlit as st
import hashlib
import os


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="EduPro | Smart Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# AUTH FILE
# =========================================================

AUTH_FILE = "auth.txt"


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =========================================================
# CREATE AUTH FILE
# =========================================================

def create_auth_file():

    if not os.path.exists(AUTH_FILE):

        admin_password = hash_password("admin123")

        with open(
            AUTH_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                f"admin|Admin|Administrator|{admin_password}\n"
            )


# =========================================================
# LOAD AUTH DATA
# =========================================================

def load_auth_data():

    create_auth_file()

    records = []

    with open(
        AUTH_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            if len(parts) != 4:
                continue

            username, role, name, password_hash = parts

            records.append(
                {
                    "username": username,
                    "role": role,
                    "name": name,
                    "password": password_hash
                }
            )

    return records


# =========================================================
# AUTHENTICATE USER
# =========================================================

def authenticate(username, password, role):

    password_hash = hash_password(password)

    records = load_auth_data()

    for record in records:

        if (
            record["username"].lower() == username.lower()
            and record["role"].lower() == role.lower()
            and record["password"] == password_hash
        ):

            return record

    return None


# =========================================================
# REGISTER USER
# =========================================================

def register_user(username, password, name):

    records = load_auth_data()

    for record in records:

        if record["username"].lower() == username.lower():

            return (
                False,
                "Username / Email already registered."
            )

    password_hash = hash_password(password)

    with open(
        AUTH_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{username}|User|{name}|{password_hash}\n"
        )

    return (
        True,
        "Registration successful. You can now login."
    )


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

if "name" not in st.session_state:
    st.session_state.name = None


# =========================================================
# LOGGED-IN ROUTING
# =========================================================

if st.session_state.logged_in:

    if st.session_state.role == "Admin":

        st.switch_page(
            "pages/admin.py"
        )

    elif st.session_state.role == "User":

        st.switch_page(
            "pages/user_dashboard.py"
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🎓 EduPro")

    st.caption("Smart Learning Platform")

    st.markdown("---")

    st.info(
        """
        **For Students**

        Find courses based on your
        interests and learning history.
        """
    )

    st.success(
        """
        **For Working Professionals**

        Improve your skills and discover
        career-focused courses.
        """
    )

    st.markdown("---")

    st.caption(
        "Student Segmentation & Personalized Course Recommendation"
    )


# =========================================================
# HERO SECTION
# =========================================================

st.title("🎓 EduPro")

st.subheader(
    "Learn Smarter. Grow Faster. Succeed Better."
)

st.write(
    """
    A smart learning platform that helps students and
    working professionals discover personalized courses
    according to their interests, behaviour and learning history.
    """
)

st.markdown("---")


# =========================================================
# FEATURES
# =========================================================

st.header("🚀 Learning Designed For You")

st.caption(
    "Choose the learning experience that fits your goals."
)


col1, col2, col3 = st.columns(3)


with col1:

    st.info(
        """
        ### 🎓 Students

        Discover courses according to your
        learning interests and previous
        course purchases.

        **Perfect for:**
        - College students
        - Beginners
        - Learners building new skills
        """
    )


with col2:

    st.success(
        """
        ### 💼 Working Professionals

        Find relevant courses to improve
        your professional skills and
        career opportunities.

        **Perfect for:**
        - Professionals
        - Career switchers
        - Skill development
        """
    )


with col3:

    st.warning(
        """
        ### 🤖 Smart Recommendations

        Get personalized course recommendations
        based on your learning behaviour.

        **Powered by:**
        - Student segmentation
        - Course history
        - Course ratings
        """
    )


st.markdown("---")


# =========================================================
# HOW IT WORKS
# =========================================================

st.header("⚡ How EduPro Works")

step1, step2, step3 = st.columns(3)


with step1:

    st.write("### 1️⃣ Create Account")

    st.write(
        "Register your EduPro account using your name, username and password."
    )


with step2:

    st.write("### 2️⃣ Explore Courses")

    st.write(
        "View available courses and your personalized learning profile."
    )


with step3:

    st.write("### 3️⃣ Get Recommendations")

    st.write(
        "Receive course recommendations based on your learning behaviour."
    )


st.markdown("---")


# =========================================================
# AUTH SECTION
# =========================================================

st.header("🔐 Get Started With EduPro")

st.caption(
    "Login to your existing account or create a new account."
)


login_tab, register_tab = st.tabs(
    [
        "🔐 Login",
        "📝 Register"
    ]
)


# =========================================================
# LOGIN
# =========================================================

with login_tab:

    st.subheader("🔐 Login to EduPro")

    login_role = st.selectbox(
        "Account Type",
        [
            "User",
            "Admin"
        ],
        key="login_role"
    )

    login_username = st.text_input(
        "Username / Email",
        placeholder="Enter your username or email",
        key="login_username"
    )

    login_password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button(
        "🚀 Login",
        use_container_width=True,
        type="primary"
    ):

        if (
            not login_username.strip()
            or not login_password
        ):

            st.error(
                "❌ Please enter username and password."
            )

        else:

            record = authenticate(
                login_username.strip(),
                login_password,
                login_role
            )

            if record:

                st.session_state.logged_in = True

                st.session_state.role = record["role"]

                st.session_state.username = record["username"]

                st.session_state.name = record["name"]

                st.success(
                    "✅ Login successful! Redirecting..."
                )

                st.rerun()

            else:

                st.error(
                    "❌ Invalid username, password or account type."
                )


# =========================================================
# REGISTER
# =========================================================

with register_tab:

    st.subheader("📝 Create Your EduPro Account")

    st.caption(
        "Registration is available for students and working professionals."
    )

    register_name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="register_name"
    )

    register_username = st.text_input(
        "Username / Email",
        placeholder="Enter username or email",
        key="register_username"
    )

    register_password = st.text_input(
        "Password",
        type="password",
        placeholder="Minimum 6 characters",
        key="register_password"
    )

    register_confirm = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
        key="register_confirm"
    )

    if st.button(
        "📝 Create Account",
        use_container_width=True,
        type="primary"
    ):

        if (
            not register_name.strip()
            or not register_username.strip()
            or not register_password
            or not register_confirm
        ):

            st.error(
                "❌ Please fill all fields."
            )

        elif register_password != register_confirm:

            st.error(
                "❌ Passwords do not match."
            )

        elif len(register_password) < 6:

            st.error(
                "❌ Password must contain at least 6 characters."
            )

        else:

            success, message = register_user(
                register_username.strip(),
                register_password,
                register_name.strip()
            )

            if success:

                st.success(
                    "✅ " + message
                )

                st.info(
                    "Go to the Login tab and login with your new account."
                )

            else:

                st.error(
                    "❌ " + message
                )


# =========================================================
# ADMIN INFORMATION
# =========================================================

st.markdown("---")

with st.expander("ℹ️ Administrator Login"):

    st.write(
        "Default administrator account:"
    )

    st.code(
        "Username: admin\nPassword: admin123"
    )

    st.warning(
        "Change the default admin password before deploying publicly."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🎓 EduPro Recommendation System"
)

st.caption(
    "Python • Pandas • Scikit-Learn • Streamlit"
)