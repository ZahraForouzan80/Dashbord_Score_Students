import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

#تنطیمات صفحه
st.set_page_config(page_title="سیستم تحلیل نمرات دانشجویان", layout="wide")

# --- استایل راست‌چین کردن ---
st.markdown("""
    <style>
    /* کل متن‌ها و placeholder ها راست‌چین بشن */
    input, textarea, select {
        direction: rtl;
        text-align: right;
    }
    label, div[data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)


# بخش دیتابیس---------------------------------------------------------------------------------------------------------------
connecting = sqlite3.connect("students.db", check_same_thread=False)
db = connecting.cursor()

# ساخت جدول فقط اگر وجود نداشته باشد
db.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    studentid TEXT,
    term TEXT,
    moadel FLOAT,
    reshte TEXT,
    course TEXT,
    score FLOAT
)
''')
connecting.commit()


#سایدبار----------------------------------------------------------------------------------------------------------------------------
Menu = ['صفحه اصلی' , 'اضافه کردن دانشجو' , 'ویرایش یا حذف دانشجو' , 'اضافه کردن دیتابیس مورد نظر' , 'هشدارها']
sidebar1 = st.sidebar.selectbox('منو انتخاب', Menu)

#صفحه اصلی--------------------------------------------------------------------------------------------------------------------------
if sidebar1 == 'صفحه اصلی':
    st.markdown("<h2 style='text-align:center;'>داشبورد نمرات دانشجویان</h2>", unsafe_allow_html=True)
    
    # خواندن داده‌ها از دیتابیس
    read_from_db = pd.read_sql_query("SELECT * FROM students", connecting)

    if read_from_db.empty:
        st.info("هنوز هیچ دانشجویی به جدول اضافه نشده است. لطفا در سایدبار اطلاعات دانشجو را اضافه کنید...")
    else:
        # ---------- چهار کارت ----------
        total_students = len(read_from_db)
        avg_moadel = round(read_from_db['moadel'].mean(), 2)
        max_moadel = read_from_db['moadel'].max()
        min_moadel = read_from_db['moadel'].min()

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>کل دانشجویان</p><p>{total_students}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>میانگین کل معدل</p><p>{avg_moadel}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>بهترین معدل</p><p>{max_moadel}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>کمترین معدل</p><p>{min_moadel}</p></div>", unsafe_allow_html=True)

        # ---------- نمودارها ----------
        st.subheader("نمودارهای تحلیلی")
        avg_moadel_per_term = read_from_db.groupby("term")["moadel"].mean().reset_index()
        fig1 = px.bar(avg_moadel_per_term, x="term", y="moadel", title="میانگین معدل در هر ترم", labels={"term":"ترم", "moadel":"میانگین معدل"})
        st.plotly_chart(fig1, use_container_width=True)

        conditions = []
        for idx, row in read_from_db.iterrows():
            if row["score"] < 10:
                conditions.append("افتاده")
            elif row["moadel"] < 12:
                conditions.append("مشروط")
            else:
                conditions.append("پاس شده")
        read_from_db["status"] = conditions

        fig2 = px.pie(read_from_db, names="status", title="وضعیت دانشجویان(افتاده/ مشروط/پاس شده)")
        st.plotly_chart(fig2, use_container_width=True)

        # ---------- جدول ----------
        st.subheader("📋 جدول اطلاعات دانشجویان")
        st.dataframe(read_from_db.set_index('id'))
          



#صفحه اضافه کردن دانشجو------------------------------------------------------------------------------------------------------------
elif sidebar1 == 'اضافه کردن دانشجو':
    st.markdown("<h2 style='text-align:center;'>اضافه کردن دانشجو به جدول</h2>", unsafe_allow_html=True)
    
    # فرم اضافه کردن دانشجو
    with st.form("فرم اضافه کردن دانشجو"):
        name = st.text_input("نام دانشجو را وارد کنید")
        studentid = st.text_input(" شماره دانشجویی دانشجو را وارد کنید")
        term = st.text_input("ترم مورد نظر")
        moadel = st.number_input("معدل دانشجو را وارد کنید", min_value=0.0, max_value=20.0)
        reshte = st.text_input("رشته دانشجو را وارد کنید")
        course = st.text_input("درس مربوطه را وارد کنید")
        score = st.number_input("نمره درس مربوطه را وارد کنید", min_value=0.0, max_value=20.0)
        submit = st.form_submit_button("اضافه کردن دانشجو به جدول")

        if submit:
            db.execute("INSERT INTO students (name, studentid, term, moadel, reshte, course, score) VALUES (?,?,?,?,?,?,?)",
                       (name, studentid, term, moadel, reshte, course, score))
            connecting.commit()
            st.success(f"دانشجو {name} با شماره دانشجویی {studentid} در درس {course} با نمره {score} اضافه شد!")
        
#صفحه ویرایش یا حذف دانشجو------------------------------------------------------------------------------------------------------------
elif sidebar1 == 'ویرایش یا حذف دانشجو':
    st.markdown("<h2 style='text-align:center;'>ویرایش یا حذف دانشجو</h2>", unsafe_allow_html=True)    

    # فیلد جستجو
    search = st.text_input("🔍 جستجو بر اساس شماره دانشجویی، نام، ترم یا درس:")

    if search:
        query = f"""
        SELECT * FROM students
        WHERE studentid LIKE '%{search}%'
        OR name LIKE '%{search}%'
        OR term LIKE '%{search}%'
        OR course LIKE '%{search}%'
        """
    else:
        query = "SELECT * FROM students"

    read_from_db = pd.read_sql_query(query, connecting)

    if read_from_db.empty:
        st.warning("هیچ نتیجه‌ای پیدا نشد.")
    else:
        st.subheader("جدول اطلاعات دانشجویان")
        for i, row in read_from_db.iterrows():
            # همه ستون‌ها نمایش داده میشن
            with st.expander(f" {row['name']} - {row['studentid']}"):
                st.write(row.to_frame().T)  # نمایش تمام ستون‌ها برای همون دانشجو

                col1, col2 = st.columns(2)

                # دکمه ویرایش
                if col1.button( ویرایش", key=f"edit_{row['id']}"):
                    st.session_state["edit_row"] = int(row["id"])
                    st.rerun()


                # دکمه حذف
                if col2.button("حذف", key=f"delete_{row['id']}"):
                    db.execute("DELETE FROM students WHERE id=?", (row["id"],))
                    connecting.commit()
                    st.success(f"دانشجو {row['name']} حذف شد")
                    st.rerun()


    # فرم ویرایش وقتی روی ویرایش کلیک میشه
    if "edit_row" in st.session_state:
        studentid_id = st.session_state["edit_row"]
        student_data = pd.read_sql_query(
            "SELECT * FROM students WHERE id=?", connecting, params=(studentid_id,)
        ).iloc[0]

        st.subheader(f"✏️ ویرایش دانشجو (ID: {studentid_id})")
        with st.form("edit_form"):
            name = st.text_input("نام", value=student_data["name"])
            studentid = st.text_input("شماره دانشجویی", value=student_data["studentid"])
            term = st.text_input("ترم", value=student_data["term"])
            moadel = st.number_input("معدل", min_value=0.0, max_value=20.0, value=float(student_data["moadel"]))
            reshte = st.text_input("رشته", value=student_data["reshte"])
            course = st.text_input("درس", value=student_data["course"])
            score = st.number_input("نمره", min_value=0.0, max_value=20.0, value=float(student_data["score"]))
            save = st.form_submit_button("ذخیره تغییرات")

            if save:
                db.execute("""
                    UPDATE students 
                    SET name=?, studentid=?, term=?, moadel=?, reshte=?, course=?, score=?
                    WHERE id=?
                """, (name, studentid, term, moadel, reshte, course, score, studentid_id))
                connecting.commit()
                st.success("✅ اطلاعات با موفقیت ویرایش شد")
                del st.session_state["edit_row"]
                st.rerun()


    


        
#صفحه اضافه کردن دیتابیس csv------------------------------------------------------------------------------------------------------------
elif sidebar1 == 'اضافه کردن دیتابیس مورد نظر':
    st.markdown("<h2 style='text-align:center;'>اضافه کردن دیتابیس مورد نظر و دیدن نتایج </h2>", unsafe_allow_html=True)  
    


#صفحه هشدار ها برای الگوریتم تشخیص ناهنجاری------------------------------------------------------------------------------------------------------------
elif sidebar1 == 'هشدارها':
    st.markdown("<h2 style='text-align:center;'>تشخیص دانشجویان با الگوهای ناهنجاری</h2>", unsafe_allow_html=True)
