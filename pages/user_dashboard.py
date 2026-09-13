import streamlit as st
import pandas as pd
from pathlib import Path


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="EduPro Student Dashboard",
    page_icon="🎓",
    layout="wide"
)
# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🎓 EduPro")
    st.write(f"Welcome, {st.session_state.get('name', 'Student')}")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.name = None

        st.switch_page("app.py")

# =====================================================
# FIND PROJECT ROOT
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# LOAD DATA SAFELY
# =====================================================

def load_csv(filename):
    file_path = BASE_DIR / filename

    if not file_path.exists():
        st.error(f"❌ File not found: {file_path}")
        st.stop()

    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"❌ Error loading {filename}: {e}")
        st.stop()


users = load_csv("users_clean.csv")
courses = load_csv("courses_clean.csv")
transactions = load_csv("transactions_clean.csv")


# =====================================================
# SESSION INFORMATION
# =====================================================

username = str(st.session_state.get("username", "") or "")
name = str(st.session_state.get("name", "") or "")


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🎓 EduPro")

logged_user = name if name else username

if logged_user:
    st.sidebar.success(f"Logged in as: {logged_user}")
else:
    st.sidebar.info("Guest User")

st.sidebar.markdown("---")

st.sidebar.write(
    "Student & Working Professional Dashboard"
)


# =====================================================
# HEADER
# =====================================================

st.title("🎓 Welcome to EduPro")

if name:
    st.subheader(f"Hello, {name}! 👋")
else:
    st.subheader("Hello! 👋")

st.write(
    "Explore courses and get personalized recommendations."
)

st.markdown("---")


# =====================================================
# CHECK REQUIRED COLUMNS
# =====================================================

required_user_columns = [
    "UserID",
    "UserName"
]

required_course_columns = [
    "CourseID",
    "CourseName",
    "CourseCategory",
    "CourseRating"
]

required_transaction_columns = [
    "UserID",
    "CourseID"
]

missing_users = [
    col for col in required_user_columns
    if col not in users.columns
]

missing_courses = [
    col for col in required_course_columns
    if col not in courses.columns
]

missing_transactions = [
    col for col in required_transaction_columns
    if col not in transactions.columns
]

if missing_users:
    st.error(
        f"❌ Missing columns in users_clean.csv: {missing_users}"
    )
    st.stop()

if missing_courses:
    st.error(
        f"❌ Missing columns in courses_clean.csv: {missing_courses}"
    )
    st.stop()

if missing_transactions:
    st.error(
        f"❌ Missing columns in transactions_clean.csv: "
        f"{missing_transactions}"
    )
    st.stop()


# =====================================================
# DASHBOARD METRICS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    total_courses = courses["CourseID"].nunique()

    st.metric(
        "📚 Total Courses",
        total_courses
    )

with col2:
    total_students = users["UserID"].nunique()

    st.metric(
        "👥 Total Students",
        total_students
    )

with col3:
    total_enrollments = len(transactions)

    st.metric(
        "💳 Total Enrollments",
        total_enrollments
    )


st.markdown("---")


# =====================================================
# COURSE EXPLORER
# =====================================================

st.header("🔎 Explore Courses")

categories = sorted(
    courses["CourseCategory"]
    .dropna()
    .astype(str)
    .unique()
)

selected_category = st.selectbox(
    "Select Course Category",
    ["All Categories"] + categories
)


if selected_category == "All Categories":

    filtered_courses = courses.copy()

else:

    filtered_courses = courses[
        courses["CourseCategory"].astype(str)
        == selected_category
    ]


display_courses = filtered_courses[
    [
        "CourseID",
        "CourseName",
        "CourseCategory",
        "CourseRating"
    ]
].sort_values(
    by="CourseRating",
    ascending=False
)


st.dataframe(
    display_courses,
    hide_index=True,
    use_container_width=True
)


st.markdown("---")


# =====================================================
# RECOMMENDATION FUNCTION
# =====================================================

def recommend_courses(user_id):

    # Find courses already purchased/enrolled
    purchased = transactions[
        transactions["UserID"] == user_id
    ].copy()

    if purchased.empty:
        return pd.DataFrame()

    # Add course information
    purchased_data = purchased.merge(
        courses[
            [
                "CourseID",
                "CourseName",
                "CourseCategory",
                "CourseRating"
            ]
        ],
        on="CourseID",
        how="left"
    )

    if purchased_data.empty:
        return pd.DataFrame()

    # Find user's preferred category
    category_mode = purchased_data[
        "CourseCategory"
    ].dropna().mode()

    if category_mode.empty:
        return pd.DataFrame()

    preferred_category = category_mode.iloc[0]

    # Courses already purchased
    purchased_ids = purchased[
        "CourseID"
    ].tolist()

    # Recommend courses from preferred category
    recommendations = courses[
        (
            courses["CourseCategory"]
            == preferred_category
        )
        &
        (
            ~courses["CourseID"].isin(purchased_ids)
        )
    ].copy()

    if recommendations.empty:
        return pd.DataFrame()

    # Highest rated first
    recommendations = recommendations.sort_values(
        by="CourseRating",
        ascending=False
    )

    return recommendations[
        [
            "CourseID",
            "CourseName",
            "CourseCategory",
            "CourseRating"
        ]
    ].head(5)


# =====================================================
# PERSONALIZED RECOMMENDATIONS
# =====================================================

st.header("⭐ Personalized Recommendations")


user_record = users[
    users["UserName"]
    .astype(str)
    .str.strip()
    .str.lower()
    ==
    username.strip().lower()
]


if not username:

    st.info(
        "ℹ️ Please login first to see personalized recommendations."
    )


elif not user_record.empty:

    user_id = user_record[
        "UserID"
    ].iloc[0]

    result = recommend_courses(user_id)

    if result.empty:

        st.info(
            "No personalized recommendations available yet."
        )

    else:

        st.success(
            "🎯 Courses recommended for you"
        )

        st.dataframe(
            result,
            hide_index=True,
            use_container_width=True
        )

else:

    st.warning(
        "⚠️ Your login account is not linked "
        "to a student profile yet."
    )


st.markdown("---")


# =====================================================
# TOP RATED COURSES
# =====================================================

st.header("🔥 Top Rated Courses")

top_courses = courses[
    [
        "CourseID",
        "CourseName",
        "CourseCategory",
        "CourseRating"
    ]
].sort_values(
    by="CourseRating",
    ascending=False
).head(10)


st.dataframe(
    top_courses,
    hide_index=True,
    use_container_width=True
)


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align: center;
        color: gray;
        padding: 20px;
    ">

        <h4>🎓 EduPro Recommendation System</h4>

        <p>
            Personalized Learning for Students & Working Professionals
        </p>

        <p>
            Developed by Aman Kumar
        </p>

    </div>
    """,
    unsafe_allow_html=True
)