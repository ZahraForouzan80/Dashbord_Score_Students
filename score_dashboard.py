import streamlit as st                         #رابط گرافیکی
import pandas as pd                            #مدیریت دیتا و داده ها
import sqlite3                                 #دیتابیس
import plotly.express as plotly                #نمودار های تعاملی
from sklearn.ensemble import IsolationForest   # الگوریتم ناهنجاری برای یادگیری ماشین
import numpy as np



#************تنطیمات اولیه صفحه************************
st.set_page_config(page_title=" سیستم تحلیل نمرات دانشجویان", page_icon="🗃", layout="wide") 
# دانلود آیکون از سایت https://www.webfx.com/tools/emoji-cheat-sheet/

def load_css(style_page):
    with open(style_page , encoding="utf-8") as style: 
        st.markdown(f"<style>{style.read()}</style>", unsafe_allow_html=True)
load_css("style.css")
# تایع برای فراخوانی فایل استایل
#with باعث میشه بعد از اینکه کار با فایل تموم شد، فایل خودکار بسته بشه 


#************بخش دیتابیس*********************************
connecting_to_database = sqlite3.connect("database_project_for_students", check_same_thread=False)
#رو میزنیم که وقتی چند نفر همزمان به دیتابیس دسترسی پیدا میکنن برنامه خطا نده check_same_thread

db= connecting_to_database.cursor()    #ساخت نشانگر برای اجرای دستورات دیتابیس

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
connecting_to_database.commit()  #یعنی ذخیره کردن commit


#************ایجاد سایدبار************************
Menu = ["صفحه‌ٔ اصلی | گزارش کلی سیستم","مدیریت و بارگذاری پایگاه‌داده‌ها","ثبت دانشجو جدید", "ویرایش / حذف اطلاعات دانشجویان", "هشدارها و تحلیل ناهنجاری‌ها","پشتیبانی"]
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
        total_students = len(read_from_database)                 #کارت نمایش کل نمودارها
        avg_all_GPA = round(read_from_database['GPA'].mean(),2)  #کارت نمایش معدل کل دانشجویان  تا 2 رقم اعشار گرد میکند //mean=معدل 
        max_GPA = read_from_database['GPA'].max()                #کارت نمایش بیشترین معدل
        min_GPA = read_from_database['GPA'].min()                #کارت نمایش کمترین معدل
        
        #ایجاد یک ردیف با 4 تا ستون برای نمایش کارت های آماری
        column1, column2, column3, column4 = st.columns(4)  

        column1.markdown (f"""<div class ="card_css"><h4>تعداد کل دانشجویان</h4><p>{total_students}</p></div>""", unsafe_allow_html=True)
        column2.markdown (f"""<div class ="card_css"><h4>میانگین معدل کل دانشجویان</h4><p>{avg_all_GPA}</p></div>""", unsafe_allow_html=True) 
        column3.markdown (f"""<div class ="card_css"><h4>بیشترین معدل دانشجویان</h4><p>{max_GPA}</p></div>""", unsafe_allow_html=True)
        column4.markdown (f"""<div class ="card_css"><h4>کمترین معدل دانشجویان</h4><p>{min_GPA}</p></div>""", unsafe_allow_html=True)
        
        #ایجاد دو ستون در یک ردیف برای نمایش نمودارها کنارهم
        column1_fig, column2_fig = st.columns(2) 
        
        #برای ساخت بخش‌های جدا استفاده میشه with
        with column1_fig:
            #داده‌ها براساس ترم دسته‌بندی و میانگین معدل هرترم حساب و رست اندکس باعث میشه نتیجه به صورت جدول معمولی نمایش داده بشه
            avg_moadel_per_term = read_from_database.groupby("Semester")["GPA"].mean().reset_index()
            
            #نموار اول:نمودار میله ای برای مشخص کردن معدل های کل در هر ترم
            fig1 = plotly.bar(avg_moadel_per_term,x="Semester",y="GPA",title="میانگین معدل در هر ترم",labels={"Semester":"ترم","GPA":"میانگین معدل"})
            st.plotly_chart(fig1, use_container_width=True)
            
        with column2_fig:      
            # استفاده از نامپای کوتاه تر و سریعه چون روش برداری داره 
            list_condition = [(read_from_database["Grade"] < 10),         # افتاده
                              (read_from_database["Grade"] >= 10) & (read_from_database["GPA"] < 12),  # مشروط
                              (read_from_database["Grade"] >= 10) & (read_from_database["GPA"] >= 12)]  # پاس شده
            
            choices = ["افتاده", "مشروط", "پاس شده"]
            read_from_database["status"] = np.select(list_condition, choices, default="نامشخص")

            #نمودار دوم: نمودار دایره ای برای مشخص کردن وضعیت کلی دانشجویان
            fig2 = plotly.pie(read_from_database,names="status", title="وضعیت دانشجویان(مشروط/افتاده/پاس شده)")
            st.plotly_chart(fig2, use_container_width=True)

        # نمایش جدول برای نمایش اطلاعات دانشجویان
        st.subheader("جدول اطلاعات دانشجویان")
        st.dataframe(read_from_database.set_index('ID'))   #DataFrame برای نمایش زیباتره 


#************صفحه اضافه کردن دیتابیس csv************************           
elif sidebar_menu == "مدیریت و بارگذاری پایگاه‌داده‌ها":
    st.markdown("<h2>پایگاه داده خود را آپلود کنید و نتایج تحلیلی را مشاهده کنید!</h2>", unsafe_allow_html=True)

    #آپلود فایل CSV
    upload_file = st.file_uploader("فایل CSV مورد نظر را وارد کنید",type="csv")

    if upload_file:
        file_csv = pd.read_csv(upload_file)
        st.success("فایل با موفقیت آپلود شد!")

        #تعریف نام‌های ممکن برای تشخیص اسم ستون‌ها درصورتی که نام‌ها باهم فرق دارد
        name_map = {
            "GPA": ["GPA", "moadel", "معدل"],
            "Full_Name": ["Full_Name", "نام", "Name", "student_name"],
            "Student_ID": ["Student_ID", "شماره دانشجویی", "ID",],
            "Class":["class","Class","کلاس","استاد","teacher"],
            "Semester": ["Semester", "ترم", "Term"," سال ورود","نیم سال ورود"],
            "Grade":["Grade", "نمره" ,"Religion", "دینی", "معارف","Kurdish", "کردی","Arabic", "عربی","English", "انگلیسی","Math", 
                      "Mathematics", "ریاضی","Computer", "کامپیوتر", "رایانه","Science", "علوم","Social", "اجتماعی","Physics", "فیزیک",
                      "Chemistry", "شیمی","Biology", "زیست","History", "تاریخ","Geography", "جغرافیا","Literature", "ادبیات","Persian", 
                      "فارسی","Statistics", "آمار", "نرم افزار توسعه موبایل","lessens","درس","دروس"], 
            "Lesson":["Religion", "دینی", "معارف","Kurdish", "کردی","Arabic", "عربی","English", "انگلیسی","Math", "Mathematics", "ریاضی",
                      "Computer", "کامپیوتر", "رایانه","Science","علوم","Social","اجتماعی","Physics","فیزیک","Chemistry","شیمی","Biology",
                      "زیست","History", "تاریخ","Geography","جغرافیا","Literature", "ادبیات","Persian", "فارسی","Statistics", "آمار",
                      "نرم افزار توسعه موبایل","lessens","درس","دروس"]}

        # تابع پیدا کردن ستون نمرات
        def find_grade_columns(df, grade_names):
            grade_cols = []                  #لیست خالی برای ذخیره ستون‌های نمره
            for col in df.columns:           #روی تک‌ تک ستون‌های فایل حرکت می‌کنه
                for name in grade_names:     #روی تمام اسم‌های ممکن درس‌ها (ریاضی،عربی، …)
                    if name.lower() in col.lower():    #بدون حساسیت به حروف بزرگ/کوچک
                        if col not in grade_cols:      #از تکراری شدن جلوگیری می‌کنه
                            grade_cols.append(col)     #نتیجه رو توی لیست خالی ذخیره میکنه
                            break
            return grade_cols
        

        #این تابع ستونی که با یکی از نام‌های احتمالی مطابقت داره رو پیدا می‌کنه
        def find_column(df, possible_names):
            for name in possible_names:
                for col in df.columns:                  #روی تک‌ تک ستون‌های فایل حرکت می‌کنه
                    if name.lower() in col.lower():     #حساسیت به حروف کوچک و بزرگ نباشد
                        return col
            return None                                 #برمی‌گردد اگر ستون پیدا نشود none


        #هر ستون مهم رو که با تابع بالا پیدا می‌کنیم در یک متغیر ذخیره می‌کنیم
        gpa_col = find_column(file_csv, name_map["GPA"])
        lesson_col = find_column(file_csv, name_map["Lesson"])
        grade_columns = find_grade_columns(file_csv, name_map["Grade"])
        
        #فقط ستون‌هایی که عددی هستن رو جدا میکنیم چه اعشاری چه صحیح
        numeric_cols = file_csv.select_dtypes(include="number").columns.tolist() 
        new_grade_columns = []
    
        #یه حلقه برای جداکردن ستون هایی که نمره دارند ولی معدل نیستند
        for c in grade_columns:
            if c in numeric_cols and c != gpa_col:
                new_grade_columns.append(c)
        grade_columns = new_grade_columns


        if not grade_columns:
            st.error("هیچ ستون نمره‌ای شناسایی نشد.")   #پیام خطا
            st.stop()

        if gpa_col is None:
            st.error("ستونی برای معدل (GPA) پیدا نشد. لطفاً نام ستون را بررسی کنید.")  #پیام خطا
        else:
            total_students = len(file_csv)                #تعداد کل دانشجویان
            avg_GPA = round(file_csv[gpa_col].mean(),2)   # کارت نمایش معدل کل دانشجویان  تا 2 رقم اعشار گرد میکند// mean=معدل 
            max_GPA = file_csv[gpa_col].max()             #کارت نمایش بیشترین معدل
            min_GPA = file_csv[gpa_col].min()             #کارت نمایش کمترین معدل

            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card_css'><h4>کل دانشجویان</h4><p>{total_students}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card_css'><h4>میانگین معدل</h4><p>{avg_GPA}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card_css'><h4>بیشترین معدل</h4><p>{max_GPA}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card_css'><h4>کمترین معدل</h4><p>{min_GPA}</p></div>", unsafe_allow_html=True)

            #درصورت وجود ستون درس ها
            if lesson_col:
                col1_fig, col2_fig = st.columns(2)
                
                with col1_fig:                
                    if grade_columns:                                   #چک می‌کنه که لیست نمرات خالی نباشه
                        df_melted = file_csv[grade_columns].copy()      #فقط ستون‌های نمره رو از دیتافریم اصلی جدا می‌کنه/copy:از تغییر ناخواسته دیتافریم اصلی جلوگیری می‌کند
                        for col in grade_columns:                       #روی تک‌ تک ستون‌های نمره حلقه می‌زنه
                            df_melted[col] = pd.to_numeric(df_melted[col], errors="coerce")  #مقادیر ستون نمره رو تبدیل می‌کنه به عدد واقعی اگه متن باشه یا خالی واینا با NaN جایگزین می‌شه  
                        df_melted = df_melted.melt(value_vars=grade_columns,var_name="درس",value_name="نمرات درسی").dropna()  #حذف مقادیر خالی dropna()//ستون‌ها، ردیف می‌شن

                        #برای نمایش تعداد دانشجویان هر درس
                        fig_hist = plotly.histogram(df_melted,x="درس",y="نمرات درسی",histfunc="count",color="درس",text_auto=True,title="هیستوگرام تعداد دانشجویان در هر درس")
                        # یعنی وقتی چند داده داخل یک ستون افتادن، باهاشون چه کاری انجام بشه histfunc
                        fig_hist.update_layout(xaxis_title="درس",yaxis_title="تعداد دانشجویان",showlegend=False)  
                        #یعنی راهنمای نمودار نمایش داده نشود showlegend=False
                        st.plotly_chart(fig_hist, use_container_width=True)


                with col2_fig:
                    #تابع تعیین وضعیت تحصیلی
                    def status_func(x):
                        if x >= 10:
                            return "قبول"
                        elif x >= 8:
                            return "مشروط"
                        else:
                            return "مردود"

                    file_csv["وضعیت تحصیلی"] = file_csv[gpa_col].apply(status_func)   #یعنی این تابع رو روی تک‌تک مقادیر معدل اجرا کن apply(status_func)
                    #اعمال تابع روی دیتافریم

                    status_counts = file_csv["وضعیت تحصیلی"].value_counts().reset_index()  # یعنی شمارش تعداد هر مقدار یکتا در یک ستون value_counts()
                    #شمردن تعداد هر وضعیت
                    status_counts.columns = ["وضعیت", "تعداد"]
                    #تغییر نام ستون‌ها

                    fig_pie = plotly.pie(status_counts,names="وضعیت",values="تعداد",title="وضعیت تحصیلی دانشجویان")
                    st.plotly_chart(fig_pie, use_container_width=True)               
                
                    

            if grade_columns:    
                selected_course = st.selectbox("بخش مورد نظر خود را انتخاب کنید:", options=sorted(grade_columns)) 
            
                #نمایش نمودار
                fig = plotly.histogram(file_csv, x=selected_course)
                fig.update_layout(title=f"هیستوگرام نمرات درس {selected_course}",xaxis_title="نمره",yaxis_title="تعداد دانشجویان")
                st.plotly_chart(fig, use_container_width=True)

                column1_baze, column2_baze = st.columns(2)
                #دو ستون برای تعیین بازی مد نظر

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
             

            #**تشخیص ناهنجاری**
            col1_normally, col2_normally, col3_normally, col4_normally  = st.columns(4)
            #چهار ستون برای انتخاب اعمال های ناهنجاری
            with col1_normally:
                if numeric_cols:
                    anomaly_column_option = st.radio("ستون انتخابی برای محاسبه ناهنجاری:",("معدل (GPA)", "نمره (Grade)"))
                    
            with col2_normally:
                missing_option = st.radio("روش برخورد با داده‌های خالی:", ("جایگزینی با 0", "پر کردن با میانه"))
                
            with col3_normally:    
                anormally_choose = st.radio("انتخاب روش محاسبه ناهنجاری:",("روش آماری","Isolation Forest"))

            with col4_normally:
                    char_type = st.radio("نوع نمودار مورد نظر:",["هیستوگرام","نمودار میله‌ای"])
    

            if anomaly_column_option == "معدل (GPA)":
                default_column = gpa_col   
            else:
                default_column = selected_course

            if missing_option == "جایگزینی با 0":
                file_csv[default_column] = file_csv[default_column].fillna(0)  #یعنی هرجا مقدار خالی دیدی 0 بذار fillna(0)
            else:
                median_val = file_csv[default_column].median()   #یعنی عدد وسط داده‌ها (نسبت به میانگین مقاوم‌تره) median()
                #محاسبه میانه ستون
                file_csv[default_column] = file_csv[default_column].fillna(median_val)    
                #هر جا مقدار خالی باشه مقدار میانه ستون قرار می‌گیره

            if anormally_choose == "روش آماری":
                mean_val = file_csv[default_column].mean()
                std_val = file_csv[default_column].std()
                file_csv["وضعیت"] = np.where(abs(file_csv[default_column] - mean_val) > 2*std_val, "ناهنجار", "نرمال")  #abs =قدر مطلق فاصله
            else:
                # انتخاب درصد ناهنجاری
                model = IsolationForest(contamination=0.1, random_state=42)
                model.fit(file_csv[[default_column]])
                #یعنی مدل الگوهای داده رو یاد بگیر fit
                #دلیل 2 تا براکت اینه که نوع داده دیتافریم باشه چون مدل داده دوبعدی میخواد نه یه لیست ساده

                file_csv["وضعیت"] = model.predict(file_csv[[default_column]])
                #model.predict(...) روی هر سطر داده اجرا می‌شه
                #تیجه این خط یه ستون جدید ساخته می‌شه به اسم وضعیت
                file_csv["وضعیت"] = file_csv["وضعیت"].map({1: "نرمال", -1: "ناهنجار"})
                #یعنی هر مقدار رو طبق دیکشنری که مینویسم جایگزین کن map
            
            nahanjar = file_csv[file_csv["وضعیت"] == "ناهنجار"]  #فیلتر کردن دیتافریم و جدا کردن ناهنجارها
            st.markdown(f"<div class='card_css'><h4>تعداد ناهنجاری‌ها</h4><p>{len(nahanjar)}</p></div>", unsafe_allow_html=True)


            if char_type == "هیستوگرام":
                fig_anormally = plotly.histogram(file_csv, x=default_column, color="وضعیت",
                                color_discrete_map={"نرمال":"blue", "ناهنجار":"red"})
                st.plotly_chart(fig_anormally, use_container_width=True) 
            else:
                df_counts = file_csv.groupby([default_column, "وضعیت"]).size().reset_index(name="تعداد")
                #داده ها رو بر اساس نمره/معدل و وضعیت که نرماله یا ناهنجار گروه بندی میکنه و تعداد هر گروه رو هم میشماره
                fig_anormally = plotly.bar(df_counts, x=default_column, y="تعداد", color="وضعیت",
                     color_discrete_map={"نرمال": "blue", "ناهنجار": "red"})
                st.plotly_chart(fig_anormally, use_container_width=True)

            st.subheader("جدول ناهنجاری‌ها")
            st.dataframe(nahanjar) 

            #*****بخش ناهنجاری روی دانشجویانی که در چند ترم نمره یا معدل دارند*****
            st.write("")   #ایجاد فاصله
            st.write("")   #ایجاد فاصله
            st.markdown(f"<div class='card_css'><h4>بخش دوم تحلیلات ناهنجاری </h4></div>", unsafe_allow_html=True)
            
            student_col = (find_column(file_csv, name_map["Student_ID"]) or find_column(file_csv, name_map["Full_Name"]))
            #حاوی نام ستونی که دانشجوها رو شناسایی می‌کنه هست student_col
            
            score_cols = grade_columns

            file_csv["تعداد_درس"] = file_csv[score_cols].notna().sum(axis=1)
            #ستون جدید "تعداد_درس" ساخته می‌شه که تعداد درس‌های ثبت‌شده هر دانشجو رو نشون می‌ده

            students_multi = file_csv[file_csv["تعداد_درس"] > 1][[student_col, "تعداد_درس"]]
            #از دیتافریم فقط دانشجوهایی که بیش از یک درس ثبت کرده‌اند را انتخاب کن و فقط ستون‌های شناسه/نام دانشجو و تعداد درس‌ها را نگه دار
            
            if students_multi.empty:
                st.info("دانشجویی با بیش از یک درس یافت نشد")
            else:
                st.subheader("دانشجویان دارای چند درس")
                st.dataframe(students_multi)
 
            select_students = st.selectbox("دانشجو یا بخش موردنظر را انتخاب کنید:",options=students_multi[student_col])

            student_dataFrame = file_csv[file_csv[student_col] == select_students]

            student_scores = (student_dataFrame[score_cols].iloc[0].dropna().reset_index())
            #برای دسترسی به سطر بر اساس شماره اندیس استفاده می‌شود iloc[]
            student_scores.columns = ["درس", "نمره"]
            #ستون‌های جدید رو قابل فهم می‌کنه
            student_scores["درس"] = student_scores["درس"].str.replace("نمره", "")
            #.str.replace("_نمره", "") → متن داخل ستون "درس" رو تغییر می‌ده
            #نمره حذف می‌شه تا فقط اسم درس باقی بمونه و آماده نمایش با نمودار هاست
  
            mean_val = student_scores["نمره"].mean()  #میانگین نمرات را محاسبه می‌کند
            std_val = student_scores["نمره"].std()    #انحراف معیار نمرات را محاسبه می‌کند

            student_scores["وضعیت"] = np.where(student_scores["نمره"] < mean_val - 2 * std_val,"افت غیرعادی","نرمال")
            #np.where(condition, value_if_true, value_if_false)
            #بررسی می‌کنه کدام نمرات خیلی پایین‌تر از میانگین هستند
            #قاعده‌ی آماری: هر چیزی بیش از ۲ انحراف معیار پایین‌تر از میانگین = غیرعادی
            chart_type_student = st.radio( "نوع نمودار عملکرد دانشجو:",
                                          ["هیستوگرام", "نمودار میله‌ای"], horizontal=True)

            # رسم نمودار
            if chart_type_student == "هیستوگرام":
                fig_student = plotly.histogram(student_scores,x="نمره",color="وضعیت",color_discrete_map={"نرمال": "blue","افت غیرعادی": "red"})
            else:
                fig_student = plotly.bar(student_scores,x="درس",y="نمره",color="وضعیت",color_discrete_map={"نرمال": "blue","افت غیرعادی": "red"})               
            st.plotly_chart(fig_student, use_container_width=True)

            st.subheader(" جزئیات عملکرد دانشجو انتخاب شده")
            st.dataframe(student_scores)
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
            db.execute("""INSERT INTO database_project_for_students (Full_Name, Student_ID, Semester, GPA, Major, Course_Name, Grade)
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
    #کوئری را روی دیتابیس مشخص‌شده اجرا کن و نتیجه را به شکل یک دیتافریم پانداس برگردان و در متغیر ذخیره کن.

    if read_from_database.empty:
        st.warning("هیچ نتیجه‌ای پیدا نشد.")
    else:
        st.info("🔹 می‌توانید اطلاعات جدول را مستقیماً ویرایش کنید یا برای حذف، تیک مربوطه را بزنید.")

        # افزودن ستون برای حذف
        read_from_database["حذف؟"] = False

        # نمایش جدول قابل ویرایش
        edited_df = st.data_editor(
            read_from_database,
            num_rows="fixed",    #کاربر نمی‌تواند ردیف جدید اضافه کند یا حذف کند
            use_container_width=True,
            key="editor_students"  # کلید یکتا برای جدول، لازم برای Streamlit.
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
