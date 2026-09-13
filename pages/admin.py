import streamlit as st
import pandas as pd
import joblib


# ===================================================
# ADMIN LOGIN PROTECTION
# ===================================================

if not st.session_state.get("logged_in", False):

    st.switch_page("app.py")


if st.session_state.get("role") != "Admin":

    st.error("❌ Access Denied")

    st.stop()

# ===================================================
# LOGOUT
# ===================================================

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.name = None

    st.switch_page("app.py")

# ===================================================
# PAGE CONFIG
# ===================================================

st.set_page_config(
    page_title="EduPro Recommendation System",
    page_icon="🎓",
    layout="wide"
)

st.title(
    "🎓 Student Segmentation & Personalized Course Recommendation System"
)

# ===================================================
# SIDEBAR
# ===================================================

st.sidebar.title("🎓 EduPro Dashboard")

st.sidebar.markdown("---")

st.sidebar.info(
    """
    ### Project

    Student Segmentation &
    Personalized Course Recommendation

    Built Using:

    ✅ Python

    ✅ Pandas

    ✅ Scikit-Learn

    ✅ Streamlit
    """
)

st.sidebar.markdown("---")

st.sidebar.success("Developed by: Aman Kumar")

st.sidebar.markdown("---")

st.sidebar.write("Version 1.0")

st.markdown("---")


# ===================================================
# LOAD DATA
# ===================================================

users = pd.read_csv("users_clean.csv")
courses = pd.read_csv("courses_clean.csv")
transactions = pd.read_csv("transactions_clean.csv")
features = pd.read_csv("final_student_clusters.csv")

cluster_model = joblib.load("cluster_model.pkl")
scaler = joblib.load("scaler.pkl")


# ===================================================
# MERGE TRANSACTIONS + COURSES
# ===================================================

recommend_data = transactions.merge(
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


# ===================================================
# DASHBOARD
# ===================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "👥 Total Users",
        users["UserID"].nunique()
    )

    st.caption("Registered Students")


with col2:

    st.metric(
        "📚 Total Courses",
        courses["CourseID"].nunique()
    )

    st.caption("Available Courses")


with col3:

    st.metric(
        "💳 Total Transactions",
        len(transactions)
    )

    st.caption("Course Transactions")


st.markdown("---")


# ===================================================
# DASHBOARD ANALYTICS
# ===================================================

st.header("📊 Dashboard Analytics")

colA, colB = st.columns(2)


with colA:

    st.subheader("📚 Course Categories")

    category_count = courses["CourseCategory"].value_counts()

    st.bar_chart(category_count)


with colB:

    st.subheader("💳 Payment Methods")

    payment_count = transactions["PaymentMethod"].value_counts()

    st.bar_chart(payment_count)


st.markdown("---")


# ===================================================
# PURCHASED COURSES FUNCTION
# ===================================================

def purchased_courses(user_id):

    purchased = recommend_data[
        recommend_data["UserID"] == user_id
    ]

    return purchased[
        [
            "CourseID",
            "CourseName",
            "CourseCategory"
        ]
    ].drop_duplicates()


# ===================================================
# STUDENT SEGMENT FUNCTION
# ===================================================

def get_student_segment(user_id):

    student = features[
        features["UserID"] == user_id
    ]

    if student.empty:

        return "Unknown"

    if "ClusterName" in student.columns:

        return student["ClusterName"].iloc[0]

    elif "Cluster" in student.columns:

        cluster = student["Cluster"].iloc[0]

        cluster_map = {
            0: "🟢 Premium Learner",
            1: "🔵 Casual Learner",
            2: "🟠 Explorer",
            3: "🟣 Advanced Learner"
        }

        return cluster_map.get(
            cluster,
            f"Cluster {cluster}"
        )

    return "Unknown"


# ===================================================
# RECOMMENDATION FUNCTION
# ===================================================

def recommend_courses(user_id):

    purchased = recommend_data[
        recommend_data["UserID"] == user_id
    ]

    # User has no purchase history
    if purchased.empty:

        return pd.DataFrame()

    # Find most preferred category
    category = purchased[
        "CourseCategory"
    ].mode()[0]

    # Already purchased course IDs
    purchased_ids = purchased[
        "CourseID"
    ].tolist()

    # Find courses from preferred category
    # excluding already purchased courses
    recommendations = courses[
        (courses["CourseCategory"] == category)
        &
        (~courses["CourseID"].isin(purchased_ids))
    ]

    # Sort by highest rating
    recommendations = recommendations.sort_values(
        by="CourseRating",
        ascending=False
    )

    # Return top 5 courses
    return recommendations[
        [
            "CourseID",
            "CourseName",
            "CourseCategory",
            "CourseRating"
        ]
    ].head(5)


# ===================================================
# USER INPUT
# ===================================================

st.header("🎯 Get Course Recommendation")

user_id = st.selectbox(
    "👤 Select User ID",
    sorted(users["UserID"].unique())
)

st.markdown("---")


# ===================================================
# RECOMMENDATION BUTTON
# ===================================================

if st.button("🚀 Recommend Courses"):

    # =================================================
    # STUDENT DETAILS
    # =================================================

    student = users[
        users["UserID"] == user_id
    ]

    if student.empty:

        st.error("❌ User Not Found")

    else:

        # =============================================
        # TWO COLUMN LAYOUT
        # =============================================

        left, right = st.columns(2)

        # ---------------------------------------------
        # LEFT COLUMN - STUDENT DETAILS
        # ---------------------------------------------

        with left:

            st.subheader("👤 Student Details")

            st.dataframe(
                student[
                    [
                        "UserID",
                        "UserName",
                        "Age",
                        "Gender"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )


        # ---------------------------------------------
        # RIGHT COLUMN - STUDENT SEGMENT
        # ---------------------------------------------

        with right:

            st.subheader("🎯 Student Segment")

            segment = get_student_segment(user_id)

            st.success(segment)


        st.markdown("---")


        # =================================================
        # PURCHASED COURSES
        # =================================================

        st.subheader("📚 Purchased Courses")

        purchased = purchased_courses(user_id)

        if purchased.empty:

            st.info(
                "ℹ️ This student has not purchased any course."
            )

        else:

            st.dataframe(
                purchased,
                hide_index=True,
                use_container_width=True
            )


        st.markdown("---")


        # =================================================
        # RECOMMENDED COURSES
        # =================================================

        st.subheader("⭐ Recommended Courses")

        result = recommend_courses(user_id)

        if result.empty:

            st.warning(
                "⚠️ No recommendations available for this user."
            )

        else:

            st.success(
                "✅ Recommended Courses"
            )

            st.dataframe(
                result,
                hide_index=True,
                use_container_width=True
            )

            # ---------------------------------------------
            # DOWNLOAD RECOMMENDATIONS
            # ---------------------------------------------

            csv = result.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 Download Recommendations",
                data=csv,
                file_name=f"{user_id}_recommendations.csv",
                mime="text/csv"
            )


        st.markdown("---")

        st.success(
            "✅ Recommendation Generated Successfully"
        )


# ===================================================
# FOOTER
# ===================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:gray;">
        <h4>
            EduPro Student Segmentation &
            Personalized Course Recommendation System
        </h4>
        <p>
            Developed using Python • Pandas •
            Scikit-learn • Streamlit
        </p>
    </div>
    """,
    unsafe_allow_html=True
)