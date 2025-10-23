import streamlit as st

import pandas as pd

import plotly.express as px

import sqlite3

from sklearn.ensemble import IsolationForest



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

                if col1.button("ویرایش", key=f"edit_{row['id']}"):

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

    

    #اپلود فایل

    uploaded_file = st.file_uploader("فایل CSV مورد نظر را وارد کنید" , type="csv")



    if uploaded_file:

        file_csv = pd.read_csv(uploaded_file)

        st.success("فایل با موفقیت آپلود شد!")



        total_students = len(file_csv)

        avg_moadel = round(file_csv['moadel'].mean(), 2)

        max_moadel = file_csv['moadel'].max()

        min_moadel = file_csv['moadel'].min()



        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>کل دانشجویان</p><p>{total_students}</p></div>", unsafe_allow_html=True)

        col2.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>میانگین معدل</p><p>{avg_moadel}</p></div>", unsafe_allow_html=True)

        col3.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>بهترین معدل</p><p>{max_moadel}</p></div>", unsafe_allow_html=True)

        col4.markdown(f"<div style='background-color:#b0b0b0; padding:20px; border-radius:10px; text-align:center; color:black'><p>کمترین معدل</p><p>{min_moadel}</p></div>", unsafe_allow_html=True)



        st.subheader(" دیتابیس مورد نطر")

        st.dataframe(file_csv)



        all_columns = file_csv.columns.tolist()

        numeric_cols = file_csv.select_dtypes(include='number').columns.tolist()



        x_axis = st.selectbox("محور X را مطابق با دسته بندی مورد نظر انتخاب کنید" , all_columns)

        if numeric_cols:

           y_axis = st.selectbox("لطفا محور Y را انتخاب کنید", numeric_cols)

        else:

           st.warning("فایل CSV شما ستون عددی ندارد!")





        st.subheader("لطفا نوع نمودار خود را انتخاب کنید!")

        char_type = st.radio("انتخاب کنید:",["نمودار میله ای" , "نمودار دایره ای"])

        

    

        #نمایش نمودارها

        if char_type == "نمودار میله ای":

            st.subheader("نمودار میله ای")

            fig = px.bar(file_csv , x = x_axis , y = y_axis , color = x_axis)

            st.plotly_chart(fig, use_container_width=True)



        elif char_type == "نمودار دایره ای":

            st.subheader("نمودار دایره ای")

            fig = px.pie(file_csv, names = x_axis, values = y_axis, title = f"{y_axis} by {x_axis}")

            st.plotly_chart(fig, use_container_width=True)  





            

        # ---------- تشخیص ناهنجاری با Isolation Forest ----------

        analysis_columns = [col for col in ["moadel", "score"] if col in file_csv.columns]



        if numeric_cols:

            col_for_analysis = st.selectbox("ستون عددی برای تشخیص ناهنجاری انتخاب کنید", analysis_columns, index=0)



            from sklearn.ensemble import IsolationForest



            # مدل یادگیری ماشین برای ناهنجاری

            model = IsolationForest(contamination=0.3, random_state=42)

            model.fit(file_csv[[col_for_analysis]])

            file_csv["وضعیت"] = model.predict(file_csv[[col_for_analysis]])

            file_csv["وضعیت"] = file_csv["وضعیت"].map({1: "نرمال", -1: "ناهنجار"})



            # شمارش ناهنجاری ها

            anomalies = file_csv[file_csv["وضعیت"] == "ناهنجار"]

            st.subheader(f"تعداد ناهنجاری‌ها: {len(anomalies)}")



            # جدول ناهنجاری‌ها

            st.subheader("📋 جدول ناهنجاری‌ها")

            st.dataframe(anomalies)



            # نمودار ناهنجاری‌ها

            st.subheader("📊 نمودار ناهنجاری‌ها")

            fig_anomaly = px.bar(file_csv, x="term", y=col_for_analysis, color="وضعیت",

                                 color_discrete_map={"نرمال": "blue", "ناهنجار": "red"},

                                 title=f"تشخیص ناهنجاری در ستون {col_for_analysis}")

            st.plotly_chart(fig_anomaly, use_container_width=True)     



    else:

        st.info("یک فایل csv آپلود کنید!!!")  

        



                







elif sidebar1 == 'هشدارها':

    st.markdown("<h2 style='text-align:center;'> دانشجویان با ناهنجاری در معدل</h2>", unsafe_allow_html=True)



    # خواندن داده‌ها از دیتابیس

    read_from_db = pd.read_sql_query("SELECT * FROM students", connecting)



    if read_from_db.empty:

        st.warning(" هنوز هیچ دانشجویی در دیتابیس ثبت نشده است.")

    else:

        # محاسبه میانگین و انحراف معیار معدل

        mean_val = read_from_db['moadel'].mean()

        std_val = read_from_db['moadel'].std()



        lower = mean_val - 1 * std_val

        upper = mean_val + 1 * std_val



        # پیدا کردن دانشجویان ناهنجار

        anomalies = read_from_db[(read_from_db['moadel'] < lower) | (read_from_db['moadel'] > upper)]



        if anomalies.empty:

            st.success(" هیچ ناهنجاری در معدل دانشجویان پیدا نشد.")

        else:

            st.error(f" تعداد {len(anomalies)} دانشجو با معدل ناهنجار پیدا شد:")

            st.dataframe(anomalies.set_index("id"))



        

            read_from_db["وضعیت"] = read_from_db["id"].isin(anomalies["id"]).map({True: "ناهنجار", False: "نرمال"})



            st.subheader("نمودار معدل دانشجویان و ناهنجارها")

            fig = px.bar(read_from_db,x="name",y="moadel",color="وضعیت",color_discrete_map={"نرمال": "blue", "ناهنجار": "red"},

            title="تشخیص ناهنجاری معدل")

            st.plotly_chart(fig, use_container_width=True)
