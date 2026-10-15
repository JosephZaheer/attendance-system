import streamlit as st
import pathlib as pt
import pandas as pd
import numpy as np
import time

################################################################################

def show_deleted(df):
    full_names = tuple(pd.read_csv(metapath)["name"])

    if len(full_names) != df.shape[0]:
        if not st.checkbox("Show Deleted Student?"):

            truth = []
            for idx in df.index:
                truth.append(df.loc[idx, "name"] in full_names)

            cleaned = df[truth]
            cleaned["roll"] = range(1, sum(truth) + 1)
            return cleaned
    
    return df

################################################################################

def mark(date, month, year, model):
    img_size = 224
    toolpath = pt.Path("/workspaces/attendance-system/tools")
    yearpath = dbpath / str(year)
    path = yearpath / f"{month}.csv"

    import tensorflow as tf
    
    if not yearpath.exists() or not path.exists():
        yearpath.mkdir(exist_ok=True)
        register = pd.read_csv(metapath)
        
    else:
        register = pd.read_csv(path)
  
    if not date in register.columns:
        register.loc[:, date] = "A"

    #tool model and load image
    #convert image to a usable format
    model = tf.keras.models.load_model(toolpath / f"{model}.keras")
    img_path = dbpath / "current_prediction_target.jpg"
    img = tf.keras.utils.load_img(img_path, target_size=(img_size, img_size))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    score = tf.nn.softmax(predictions[0])

    classes = list(register["name"])
    student = classes[np.argmax(score)]

    st.write("Predicted Student:", student)
    st.write(f"Confidence: {100*np.max(score):.2f}%")
    
    student_idx = list(register.index)
    idx = student_idx[np.argmax(score)] 
    
    register.loc[idx, date] = "P"            
    register.to_csv(path, index=False)

    st.table(register)
    
################################################################################

def view(month, year, date):
    path = dbpath / f"{year}/{month}.csv"
    
    if not path.exists():
        st.error(f"No records available for {month} {year}")
        return None
        
    register = pd.read_csv(path)

    if date != "0":
        if date in register.columns:
            columns = ["roll", "name", date]
            register = register[columns]
            
        else:
            st.error(f"Attendance not availabe for this date: {date}")    
            return None

    show = show_deleted(register)
    show = show.set_index(show["roll"]).drop("roll", axis=1)
    st.dataframe(show)
    
################################################################################

def percent(months, year):
    df = pd.read_csv(metapath)
    df["Total"] = ""
    working_days = 0
                
    for month in months:
        path = dbpath / f"{year}/{month}.csv"
                    
        if not path.exists():
            continue
        
        register = pd.read_csv(path)

        #register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            df["Total"] += register[column]

    if working_days == 0:
        st.error("No attendance for the given month(s)")
        return None

    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(df["Total"]):
        df.loc[idx, "Total"] = str(row.count("P"))
        df.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"

    st.caption(f"Working days: {working_days}")
    show = df.set_index(df["roll"]).drop("roll", axis=1)
    show = show_deleted(show)
    st.dataframe(show)
    
################################################################################

def make_changes(month, year):
    path = dbpath / f"{year}/{month}.csv"
    
    if not path.exists():
        st.error(f"No records available for {month} {year}")
        return None
        
    register = pd.read_csv(path)
    register = show_deleted(register)
    editable_df = st.data_editor(register)

    if st.button("**Make Changes?**"):
        editable_df.to_csv(path, index=False)
        st.success("Register changed!")
        
################################################################################
        
def remove():
    register = pd.read_csv(metapath)

    names, options = [], []
    for idx, name in enumerate(register["name"]):
        names.append(name)
        options.append(f"{idx+1}. {name}")
    
    name = st.selectbox("Select a student:", options)
    
    if len(names) == 0:
        st.error("No students registered")
        return None

    if st.button(":red[**DELETE**]"):
        index_remove = options.index(name)
        names_length = len(names.index)
        
        names = names.drop(index_remove, axis=0)
        names.iloc[index_remove:, 0] -= 1
        names = names.set_index(range(names_length))
        names.to_csv(metapath)

        st.success("Deletion Successful!")
        show = names.set_index(show["roll"]).drop("roll", axis=1)
        st.table(show)

################################################################################
    
def order_months(unordered_months):
    full_months = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]

    ordered_months = []
    for month in full_months:
        if month in unordered_months:
            ordered_months.append(month)

    return ordered_months

################################################################################

def sidebar():
    day, date, month, year = time.strftime("%A %d %B %Y").split()
    
    st.sidebar.write(
        f"""It's **{day}**,
        {date} {month} {year}"""
        )
        
    st.sidebar.divider()
    page = st.sidebar.radio("", options)
    return page, date, month, year
            
################################################################################

dbpath = pt.Path("/workspaces/attendance-system/database")

options = [
    "Home",
    "Mark Attendance",
    "View Attendance",
    "Total Attendance",
    "Make Changes",
    "Remove Student",
    ]
    
st.title(":violet[AI ATTENDANCE SYSTEM]")
st.divider()

page, date, month, year = sidebar()
metapath = dbpath / "metadata.csv"

years = [year.name for year in dbpath.iterdir() if year.is_dir()]

years.sort(reverse=True)

if page == options[0]: #home
    import home

elif page == options[1]: #mark attendance
    img = st.camera_input("Take a photo: ")

    if img:
        st.success("Capture successful!")
        with open(dbpath / "current_prediction_target.jpg", "wb") as f:
            f.write(img.getbuffer())

        mark(date, month, year, model="model2")
            
elif page == options[2]: #view attendance register
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Select a year:", years, index=None)
    
    with col2:
        if year:
            path = dbpath / str(year)
            months = [month.stem for month in path.iterdir()]
            months = order_months(months)
            month = st.selectbox("Select a month:", months, index=None)

            date = st.slider("Specify a date:", min_value=0, max_value=31, step=1)
            st.caption("Zero for entire month")


    if year and month:
        view(month, year, str(date))

elif page == options[3]: #view attendance total and percentage    
    year = st.selectbox("Select a year:", years)
    path = dbpath / str(year)
    months = [month.stem for month in path.iterdir()]
    months = order_months(months)
    
    col1, col2 = st.columns(2)
    with col1:
        start_month = st.selectbox("Select starting month:", months, key="month1")
        start = months.index(start_month)

    with col2:
        stop_month = st.selectbox("Select ending month:", months[start:], key="month2")
        stop = months.index(stop_month) + 1

    selected_months = months[start:stop]
        
    if selected_months:
        percent(selected_months, year)

elif page == options[4]: #make changes to a register

    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Select a year:", years, index=None)
        
    with col2:
        if year:
            path = dbpath / str(year)
            months = [month.stem for month in path.iterdir()]
            months = order_months(months)
            month = st.selectbox("Select a month:", months, index=None)

    if year and month:
        make_changes(month, year)

elif page == options[5]: #remove a student
    remove()



            
