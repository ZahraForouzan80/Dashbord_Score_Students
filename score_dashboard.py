import streamlit as st                         #رابط گرافیکی
import pandas as pd                            #مدیریت دیتا و داده ها
import sqlite3                                 #دیتابیس
import plotly.express as plotly                #نمودار های تعاملی
from sklearn.ensemble import IsolationForest   # الگوریتم ناهنجاری برای یادگیری ماشین
import numpy as np



#************تنطیمات صفحه************************
st.set_page_config(page_title=" سیستم تحلیل نمرات دانشجویان", page_icon="🗃", layout="wide")   # دانلود آیکون از سایت https://www.webfx.com/tools/emoji-cheat-sheet/


def load_css(style_page):
    with open(style_page , encoding="utf-8") as style:   #with باعث میشه بعد از اینکه کار با فایل تموم شد، فایل خودکار بسته بشه  
        st.markdown(f"<style>{style.read()}</style>", unsafe_allow_html=True)

load_css("style.css")



#************ایجاد و بخش دیتابیس**********************
connecting_to_database = sqlite3.connect("database_project_for_students", check_same_thread=False)    #اینو میزنیم که وقتی چند نفر همزمان به دیتابیس دسترسی پیدا میکنن برنامه خطا نده
db= connecting_to_database.cursor()  #ساخت نشانگر برای اجرای دستورات دیتابیس

#ساخت جدول درصورت عدم وجود
#execute = اجرای دستورات
db.execute('''CREATE TABLE IF NOT EXISTS database_project_for_students(
           ID INTEGER PRIMARY KEY AUTOINCREMENT,
           Full_Name TEXT,      
           Student_ID TEXT,
           Semester TEXT,
           GPA FLOAT,
           Major TEXT,
           Course_Name TEXT,
           Grade FLOAT)''')
connecting_to_database.commit()     #commit یعنی ذخیره کردن



#************ایجاد سایدبار************************
Menu = ["صفحه‌ٔ اصلی | گزارش کلی سیستم","مدیریت و بارگذاری پایگاه‌داده‌ها","ثبت دانشجو جدید",
        "ویرایش / حذف اطلاعات دانشجویان", "هشدارها و تحلیل ناهنجاری‌ها","پشتیبانی"]
sidebar_menu = st.sidebar.selectbox("لطفاً بخش مورد نظر را انتخاب کنید", Menu)



#************صفحه اصلی ************************
if sidebar_menu == "صفحه‌ٔ اصلی | گزارش کلی سیستم":
    st.markdown("<h2>گزارش کلی سیستم و تحلیل نمرات دانشجویان</h2>", unsafe_allow_html=True)

    #خواندن داده ها از دیتابیس
    read_from_database = pd.read_sql_query("SELECT * FROM database_project_for_students" , connecting_to_database)
    
    if read_from_database.empty:
        st.info("هنوز هیچ دانشجویی به جدول اضافه نشده است. لطفا در سایدبار اطلاعات دانشجو را اضافه کنید...")
    else:
        #چهار کارت اصلی
        total_students = len(read_from_database)                   #کارت نمایش کل نمودارها
        avg_all_GPA = round(read_from_database['GPA'].mean(),2)    #کارت نمایش معدل کل دانشجویان  تا 2 رقم اعشار گرد میکند.mean=معدل 
        max_GPA = read_from_database['GPA'].max()                  #کارت نمایش بیشترین معدل
        min_GPA = read_from_database['GPA'].min()                  #کارت نمایش کمترین معدل
        
        #ایجاد یک ردیف با 4 تا ستون برای نمایش کارت های آماری
        column1, column2, column3, column4 = st.columns(4)  

        column1.markdown (f"""<div class ="card_css">
                          <h4>تعداد کل دانشجویان</h4>
                          <p>{total_students}</p></div>""", unsafe_allow_html=True)
        
        column2.markdown (f"""<div class ="card_css">
                          <h4>میانگین معدل کل دانشجویان</h4>
                          <p>{avg_all_GPA}</p></div>""", unsafe_allow_html=True) 
        
        column3.markdown (f"""<div class ="card_css">
                          <h4>بیشترین معدل دانشجویان</h4>
                          <p>{max_GPA}</p></div>""", unsafe_allow_html=True)
        
        column4.markdown (f"""<div class ="card_css">
                          <h4>کمترین معدل دانشجویان</h4>
                          <p>{min_GPA}</p></div>""", unsafe_allow_html=True)
        

        #***نمودار ها***
        column1_fig, column2_fig = st.columns(2)      # ایجاد دو ستون در یک ردیف برای نمایش نمودار ها کنار هم
        
        with column1_fig:       #نموار اول:نمودار میله ای برای مشخص کردن معدل های کل در هر ترم
            #داده‌ها را بر اساس ترم دسته‌بندی و میانگین معدل هر ترم را حساب  و رست اندکس باعث میشه نتیجه به صورت جدول معمولی تبدیل بشه
            avg_moadel_per_term = read_from_database.groupby("Semester")["GPA"].mean().reset_index()
            
            fig1 = plotly.bar(avg_moadel_per_term, x="Semester", y="GPA", title="میانگین معدل در هر ترم",
                  labels={"Semester": "ترم", "GPA": "میانگین معدل"})
            st.plotly_chart(fig1, use_container_width=True)
            

        #نمودار دوم: نمودار دایره ای برای مشخص کردن وضعیت کلی دانشجویان
        with column2_fig:        # with = برای ساخت بخش‌های جدا استفاده میشه
            # استفاده از نامپای چون کوتاه تره و سریعه چون روش برداری داره 
            list_condition = [(read_from_database["Grade"] < 10),                             # افتاده
                              (read_from_database["Grade"] >= 10) & (read_from_database["GPA"] < 12),  # مشروط
                              (read_from_database["Grade"] >= 10) & (read_from_database["GPA"] >= 12)]  # پاس شده

            choices = ["افتاده", "مشروط", "پاس شده"]

            read_from_database["status"] = np.select(list_condition, choices, default="نامشخص")


            fig2 = plotly.pie(read_from_database, names="status", title=" وضعیت دانشجویان(مشروط/افتاده/پاس شده)")
            st.plotly_chart(fig2, use_container_width=True)

        # نمایش جدول برای نمایش اطلاعات دانشجویان
        st.subheader("جدول اطلاعات دانشجویان")
        st.dataframe(read_from_database.set_index('ID'))     # id را به عنوان اندیس DataFrame می‌گذارد تا نمایش زیباتر شود. 




#************صفحه اضافه کردن دیتابیس csv************************           
elif sidebar_menu == "مدیریت و بارگذاری پایگاه‌داده‌ها":
    st.markdown("<h2>پایگاه داده خود را آپلود کنید و نتایج تحلیلی را مشاهده کنید!</h2>", unsafe_allow_html=True)

    #آپلود فایل CSV
    upload_file = st.file_uploader("فایل CSV مورد نظر را وارد کنید" , type="csv")

    if upload_file:
        file_csv = pd.read_csv(upload_file)
        st.success("فایل با موفقیت آپلود شد!")

        #تعریف نام‌های ممکن برای ستون‌ها/ دیکشنری
        name_map = {
            "GPA": ["GPA", "moadel", "معدل"],
            "Full_Name": ["Full_Name", "نام", "Name", "student_name"],
            "Student_ID": ["Student_ID", "شماره دانشجویی", "ID"],
            "Semester": ["Semester", "ترم", "Term"],
            "Grade": ["Grade", "نمره","Religion", "دینی", "معارف","Kurdish", "کردی",
                      "Arabic", "عربی","English", "انگلیسی","Math", "Mathematics", "ریاضی",
                      "Computer", "کامپیوتر", "رایانه","Science", "علوم","Social", "اجتماعی",
                      "Physics", "فیزیک","Chemistry", "شیمی","Biology", "زیست","History", "تاریخ","Geography", "جغرافیا",
                      "Literature", "ادبیات","Persian", "فارسی","Statistics", "آمار"]
        }

        def find_grade_columns(df, grade_names):
            grade_cols = []                  #لیست خالی برای ذخیره ستون‌های نمره
            for col in df.columns:           #روی تک‌تک ستون‌های فایل CSV حرکت می‌کنه
                for name in grade_names:     #وی تمام اسم‌های ممکن درس‌ها (ریاضی،عربی، …)
                    if name.lower() in col.lower():    #بدون حساسیت به حروف بزرگ/کوچک
                        if col not in grade_cols:      #از تکراری شدن جلوگیری می‌کنه
                            grade_cols.append(col)
                            break
            return grade_cols

        
         #این تابع ستونی که با یکی از نام‌های احتمالی مطابقت دارد را پیدا می‌کند
        def find_column(df, possible_names):
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in col.lower():     #حساسیت به حروف کوچک و بزرگ نباشد
                        return col
            return None                                 #گر ستون پیدا نشود، None برمی‌گردد


        #هر ستون مهم را با تابع بالا پیدا می‌کنیم و در یک متغیر ذخیره می‌کنیم.
        gpa_col = find_column(file_csv, name_map["GPA"])
        name_col = find_column(file_csv, name_map["Full_Name"])
        id_col = find_column(file_csv, name_map["Student_ID"])
        semester_col = find_column(file_csv, name_map["Semester"])
        grade_columns = find_grade_columns(file_csv, name_map["Grade"])
        
        numeric_cols = file_csv.select_dtypes(include="number").columns.tolist()  #فقط ستون‌هایی که عددی هستن
        grade_columns = [c for c in grade_columns if c in numeric_cols and c != gpa_col]

        # اگر درسی پیدا نشد
        if not grade_columns:
            st.error("هیچ ستون نمره‌ای شناسایی نشد.")
            st.stop()


        # بررسی ستون‌های ضروری
        if gpa_col is None:
            st.error("ستونی برای معدل (GPA) پیدا نشد. لطفاً نام ستون را بررسی کنید.")  #پیام خطا
        else:
            # کارت‌ها
            total_students = len(file_csv)                #تعداد کل دانشجویان
            avg_GPA = round(file_csv[gpa_col].mean(),2)   # کارت نمایش معدل کل دانشجویان  تا 2 رقم اعشار گرد میکند.mean=معدل 
            max_GPA = file_csv[gpa_col].max()
            min_GPA = file_csv[gpa_col].min()

            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card_css'><h4>کل دانشجویان</h4><p>{total_students}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card_css'><h4>میانگین معدل</h4><p>{avg_GPA}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card_css'><h4>بیشترین معدل</h4><p>{max_GPA}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card_css'><h4>کمترین معدل</h4><p>{min_GPA}</p></div>", unsafe_allow_html=True)

            
            selected_course = st.selectbox("درس مورد نظر خود را انتخاب کنید:",
                options=sorted(grade_columns)
                ) 
            

            #نمایش نمودار
            fig = plotly.histogram(file_csv, x=selected_course)
            fig.update_layout(title=f"هیستوگرام نمرات درس {selected_course}",xaxis_title="نمره",yaxis_title="تعداد دانشجویان")
            st.plotly_chart(fig, use_container_width=True)


            column1_baze, column2_baze = st.columns(2)
            with column1_baze:
                # دریافت بازه دلخواه از کاربر
                min_input = st.number_input("عدد شروع بازه:", min_value=0, max_value=100, value=0)
            with column2_baze:
                max_input = st.number_input("عدد پایان بازه:", min_value=0, max_value=100, value=100)

            # فیلتر کردن دانشجویان در بازه مشخص شده
            students_in_range = file_csv[(file_csv[selected_course] >= min_input) & (file_csv[selected_course] <= max_input)]

            # نمایش جدول
            st.subheader(f"دانشجویان درس {selected_course} با نمره بین {min_input} تا {max_input}")
            st.dataframe(students_in_range)


            #*****تشخیص ناهنجاری با Isolation Forest*****
            col1_normally, col2_normally, col3_normally, col4_normally  = st.columns(4)
            with col1_normally:
                if numeric_cols:
                    anomaly_column_option = st.radio("ستون انتخابی برای محاسبه ناهنجاری:",
                                                     ("معدل (GPA)", "نمره (Grade)"))
                    
            with col2_normally:
                missing_option = st.radio("روش برخورد با داده‌های خالی:", 
                              ("جایگزینی با 0", "پر کردن با میانگین/میانه"))
                
            with col3_normally:    
                anormally_choose = st.radio("انتخاب روش محاسبه ناهنجاری:",("روش آماری","Isolation Forest"))

            with col4_normally:
                    char_type = st.radio("نوع نمودار مورد نظر:",["هیستوگرام","نمودار میله‌ای"])
    
            if anomaly_column_option == "معدل (GPA)":
                default_column = gpa_col   
            else:
                default_column = selected_course

            if missing_option == "جایگزینی با 0":
                file_csv[default_column] = file_csv[default_column].fillna(0)
            else:
                # جایگزینی با میانگین یا میانه
                median_val = file_csv[default_column].median()
                file_csv[default_column] = file_csv[default_column].fillna(median_val)    

            if anormally_choose == "روش آماری":
                mean_val = file_csv[default_column].mean()
                std_val = file_csv[default_column].std()
                file_csv["وضعیت"] = np.where(abs(file_csv[default_column] - mean_val) > 2*std_val, "ناهنجار", "نرمال")
            else:
                # انتخاب درصد ناهنجاری
                model = IsolationForest(contamination='auto', random_state=42)
                model.fit(file_csv[[default_column]])


                file_csv["وضعیت"] = model.predict(file_csv[[default_column]])
                file_csv["وضعیت"] = file_csv["وضعیت"].map({1: "نرمال", -1: "ناهنجار"})

            nahanjar = file_csv[file_csv["وضعیت"] == "ناهنجار"]
            st.markdown(f"<div class='card_css'><h4>تعداد ناهنجاری‌ها</h4><p>{len(nahanjar)}</p></div>", unsafe_allow_html=True)

            if char_type == "هیستوگرام":
                fig_anormally = plotly.histogram(file_csv, x=default_column, color="وضعیت",
                                color_discrete_map={"نرمال":"blue", "ناهنجار":"red"})
                st.plotly_chart(fig_anormally, use_container_width=True) 
            else:
                df_counts = file_csv.groupby([default_column, "وضعیت"]).size().reset_index(name="تعداد")
                fig_anormally = plotly.bar(df_counts, x=default_column, y="تعداد", color="وضعیت",
                     color_discrete_map={"نرمال": "blue", "ناهنجار": "red"})
                st.plotly_chart(fig_anormally, use_container_width=True)

            st.subheader("جدول ناهنجاری‌ها")
            st.dataframe(nahanjar)    
    else:
        st.info("یک فایل csv آپلود کنید!!!")    

#************صفحه اضافه کردن دانشجو************************           
elif sidebar_menu == "ثبت دانشجو جدید":
    st.markdown("<h2>اضافه کردن دانشجو جدید به لیست</h2>", unsafe_allow_html=True)

    #فرم اضافه کردن دانشجو
    with st.form("فرم اضافه کردن دانشجو جدید"):
        name = st.text_input("نام دانشجو را وارد کنید!")
        studentID = st.text_input("شماره دانشجویی دانشجو را وارد کنید!")
        semester = st.text_input("ترم مورد نظر را وارد کنید!")
        gpa = st.number_input("معدل دانشجو را وارد کنید!", min_value = 0.0, max_value = 20.0, step=0.1)
        marjor = st.text_input("رشته مورد نظر را وارد کنید!")
        course = st.text_input("درس مربوطه را وارد کنید!")
        grade = st.number_input("نمره درس مربوطه را وارد کنید!", min_value = 0.0, max_value = 20.0, step=0.1)

        submit = st.form_submit_button("اضافه کردن دانشجو به لیست")

        if submit:
            db.execute("""
                INSERT INTO database_project_for_students 
            (Full_Name, Student_ID, Semester, GPA, Major, Course_Name, Grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (name, studentID, semester, gpa, marjor, course, grade))

            connecting_to_database.commit()
            st.success(f"دانشجو {name} با شماره دانشجویی {studentID} در درس {marjor} با نمره {grade} اضافه شد!")    




#************صفحه ویرایش یا حذف دانشجو***********************
elif sidebar_menu == "ویرایش / حذف اطلاعات دانشجویان":
    st.markdown("<h2>میتوانید اطلاعات دانشجو مورد نظر را ویرایش یا حذف کنید!</h2>", unsafe_allow_html=True)
    
    #***بخش جستجو***
    search = st.text_input("جستجو بر اساس شماره دانشجویی، نام، ترم یا درس:")

    if search:
        query = f"""SELECT * FROM database_project_for_students
        WHERE Student_ID LIKE '%{search}%'
        OR Full_Name LIKE '%{search}%'
        OR Semester LIKE '%{search}%'
        OR Course_Name LIKE '%{search}%'"""
    else:
        query = "SELECT * FROM database_project_for_students" 

    read_from_database = pd.read_sql_query(query, connecting_to_database)

    if read_from_database.empty:
        st.warning("هیچ نتیجه‌ای پیدا نشد.")
    else:
        st.info("🔹 می‌توانید اطلاعات جدول را مستقیماً ویرایش کنید یا برای حذف، تیک مربوطه را بزنید.")

        # افزودن ستون برای حذف
        read_from_database["حذف؟"] = False

        # نمایش جدول قابل ویرایش
        edited_df = st.data_editor(
            read_from_database,
            num_rows="fixed",    #تعداد ردیف‌ها ثابت باشد.
            use_container_width=True,
            key="editor_students"  #ک کلید یکتا برای جدول، لازم برای Streamlit.
        )

        # دکمه‌ها
        col1, col2 = st.columns(2)

        #دکمه ذخیره تغییرات
        with col1:
            if st.button("ذخیره تغییرات"):
                #فقط ردیف‌هایی که تیک حذف ندارند ذخیره شوند
                #[edited_df["حذف؟"] == False] یعنی فقط ردیف‌هایی که کاربر تیک حذف نزده انتخاب شوند.
                #drop(columns="حذف؟") ستون "حذف؟" را از DataFrame حذف می‌کند، چون دیگر نیاز نداریم این ستون در دیتابیس ذخیره شود.
                final_df = edited_df[edited_df["حذف؟"] == False].drop(columns="حذف؟")

                #پاک‌سازی جدول و بازنویسی جدید
                db.execute("DELETE FROM database_project_for_students")
                connecting_to_database.commit()

                #if_exists="append" یعنی اگر جدول وجود داشت، داده‌ها به آن اضافه شود. چون قبلاً جدول را پاک کردیم، این عمل جدول جدیدی ایجاد می‌کند.
                #index=False یعنی شماره ردیف DataFrame به عنوان ستون در دیتابیس ذخیره نشود.
                #عمل اضافه کردن به دیتابیس توسط pandas و SQLAlchemy پشت صحنه انجام می‌شود(با to_sql)
                final_df.to_sql("database_project_for_students", connecting_to_database, if_exists="append", index=False)
                st.success("✅ تغییرات با موفقیت ذخیره شدند!")
        
        
        #دکمه حذف تکی
        with col2:
            if st.button("حذف موارد تیک‌ خورده"):
                deleted_df = edited_df[edited_df["حذف؟"] == True]
                if not deleted_df.empty:
                    for i in deleted_df["Student_ID"]:
                        #این حلقه هر ردیف انتخاب شده را بر اساس شماره دانشجویی (Student_ID) از دیتابیس پاک می‌کند.
                        #? برای جلوگیری از SQL Injection استفاده می‌شود و مقدار i به آن داده می‌شود.
                        db.execute("DELETE FROM database_project_for_students WHERE Student_ID=?", (i,))
                    connecting_to_database.commit() 
                    st.success(" ردیف‌های انتخاب‌شده حذف شدند!") 
                    st.rerun()
                else:
                    st.warning(" هیچ ردیفی برای حذف انتخاب نشده است.")






#************هشدارها و تحلیل ناهنجاری‌ها************************    
elif sidebar_menu == "هشدارها و تحلیل ناهنجاری‌ها":
    st.markdown("<h2>نمایش هشدارها و نمودار تحلیل دانشجویانی که در دیتابیس سیستم ثبت شده‌اند</h2>", unsafe_allow_html=True)

    # خواندن داده‌ها از دیتابیس
    read_from_database = pd.read_sql_query("SELECT * FROM database_project_for_students", connecting_to_database)

    if read_from_database.empty:
        st.warning(" هنوز هیچ دانشجویی در دیتابیس سیستم ثبت نشده است.")
    else:
        field = st.selectbox("فیلد برای تحلیل ناهنجاری:", ["GPA", "Grade"])

        # محاسبه میانگین و انحراف معیار معدل
        mean_val = read_from_database[field].mean()
        std_val = read_from_database[field].std()

        lower = mean_val - 1  * std_val    #حدود 1 انحراف معیار دور از میانگین
        upper = mean_val + 1  * std_val

        # پیدا کردن دانشجویان ناهنجار
        anomalies = read_from_database[(read_from_database[field] < lower) | (read_from_database[field] > upper)]  #| عملگر OR منطقی در pandas 

        if anomalies.empty:
            st.success(f"هیچ ناهنجاری در {field} پیدا نشد.")
        else:
            st.error(f"تعداد {len(anomalies)} دانشجو با {field} ناهنجار پیدا شد:")
            st.dataframe(anomalies.set_index("ID"))

        
            read_from_database["وضعیت"] = read_from_database["ID"].isin(anomalies["ID"]).map({True: "ناهنجار", False: "نرمال"})  #isin برای بررسی اینکه هر id در لیست idهای anomalies هست یا نه///map  برای جایگزینی مقادیر True/False با رشته‌های مورد نظر

            st.subheader("نمودار معدل دانشجویان و ناهنجارها")
            fig = plotly.bar(read_from_database, x="Full_Name", y=field, color="وضعیت",
            title="تشخیص ناهنجاری معدل")
            st.plotly_chart(fig, use_container_width=True)        



#*************پشتیبانی*********************** 
elif sidebar_menu == "پشتیبانی":
    st.markdown("<h2>پشتیبانی و تماس با ما</h2>", unsafe_allow_html=True)

    # بارگذاری CSS
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown('<div class="support-container">', unsafe_allow_html=True)

    # فرم پشتیبانی
    with st.form("support_form"):
        st.markdown("<h2>فرم تماس با پشتیبانی</h2>", unsafe_allow_html=True)
        user_name = st.text_input("نام و نام خانوادگی")
        user_email = st.text_input("ایمیل")
        user_message = st.text_area("پیام خود را وارد کنید")

        submit_support = st.form_submit_button("ارسال پیام")

        if submit_support:
            # اینجا می‌توانی پیام را ذخیره یا به ایمیل ارسال کنی
            st.markdown('<div class="support-success">پیام شما با موفقیت ارسال شد! متشکریم.</div>', unsafe_allow_html=True)
