import streamlit as st
from datetime import datetime, timedelta, time
import calendar
import pandas as pd

# Helper function to render the calendar for the selected month
def render_calendar(month, year):
    st.write(f"### {calendar.month_name[month]} {year}")
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    month_days = calendar.monthcalendar(year, month)

    table = []
    for week in month_days:
        row = []
        for day in week:
            row.append(day if day != 0 else "")
        table.append(row)

    df = pd.DataFrame(table, columns=weekdays)
    return df

# Display and interact with the tasks for a selected date
def log_task_for_date(selected_date):
    if selected_date not in st.session_state:
        st.session_state[selected_date] = []

    st.write(f"### Tasks for {selected_date}")

    task = st.text_input("Enter a task", key=f"task_input_{selected_date}")
    category = st.selectbox("Select Category", ["Work", "Personal", "Urgent", "Other"], key=f"category_select_{selected_date}")
    priority = st.selectbox("Select Priority", ["High", "Medium", "Low"], key=f"priority_select_{selected_date}")
    due_date = st.date_input("Select Due Date", min_value=datetime.today(), key=f"due_date_input_{selected_date}")

    # Custom time selection with 24-hour dropdown
    time_options = [time(hour=h, minute=m).strftime("%H:%M") for h in range(24) for m in (0, 30)]
    selected_time_str = st.selectbox(
        "Select Due Time",
        options=time_options,
        index=time_options.index("09:00"),
        key=f"due_time_input_{selected_date}"
    )
    due_time = datetime.strptime(selected_time_str, "%H:%M").time()

    if st.button("Add Task", key=f"add_task_button_{selected_date}"):
        task_info = {
            "task": task,
            "category": category,
            "priority": priority,
            "due_date": str(due_date),
            "due_time": str(due_time),
            "completed": False,
        }
        if task_info not in st.session_state[selected_date]:
            st.session_state[selected_date].append(task_info)
            st.success("Task added!")
        else:
            st.warning("Task already exists!")

    if st.session_state[selected_date]:
        st.write("**Current Tasks:**")
        task_df = pd.DataFrame(st.session_state[selected_date])
        task_df = task_df.sort_values(by=["priority", "due_date", "due_time"], ascending=[True, True, True])

        for idx, row in task_df.iterrows():
            task_str = f"{row['task']} - Category: {row['category']} | Priority: {row['priority']} | Due: {row['due_date']} {row['due_time']}"
            if row['completed']:
                task_str = f"✅ {task_str}"
            st.write(task_str)
            mark_as_completed = st.checkbox(
                f"Mark as completed", 
                key=f"complete_{selected_date}_{idx}", 
                value=row['completed']
            )
            if mark_as_completed and not row['completed']:
                st.session_state[selected_date][idx]["completed"] = True
                st.success(f"Task '{row['task']}' marked as completed!")

# Search and view tasks by date without needing to type
def view_tasks_by_date():
    st.write("## 🔍 View Tasks by Date")
    selected = st.date_input("Pick a Date to View Tasks", value=datetime.today())
    selected_str = str(selected)
    tasks = st.session_state.get(selected_str, [])

    if tasks:
        st.write(f"### Tasks for {selected_str}")
        for idx, task in enumerate(tasks):
            with st.expander(f"{'✅ ' if task['completed'] else ''}{task['task']}"):
                st.write(f"**Category:** {task['category']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Due Date:** {task['due_date']}")
                st.write(f"**Due Time:** {task['due_time']}")
                st.write(f"**Completed:** {'Yes ✅' if task['completed'] else 'No ❌'}")
    else:
        st.info("No tasks logged for this date.")

# Highlight today's date
def highlight_today(month, year):
    today = datetime.today()
    if today.month == month and today.year == year:
        return today.day
    return None

# Generate CSV data for tasks
def get_task_csv(scope, selected_date):
    tasks = []
    for date, task_list in st.session_state.items():
        if isinstance(task_list, list):
            if scope == "day" and date == selected_date:
                tasks.extend(task_list)
            elif scope == "month" and date.startswith(selected_date[:7]):
                tasks.extend(task_list)
            elif scope == "year" and date.startswith(selected_date[:4]):
                tasks.extend(task_list)
    df = pd.DataFrame(tasks)
    return df.to_csv(index=False)

# Main Streamlit app with sidebar
def main():
    # Apply custom CSS to set light grey background
    st.markdown(
    """
    <style>
        /* Main background */
        [data-testid="stAppViewContainer"] {
            background-image: url('https://png.pngtree.com/thumb_back/fh260/background/20240916/pngtree-simple-orange-aesthetic-background-image_16213466.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }

        /* Sidebar background */
        [data-testid="stSidebar"] > div:first-child {
            background-image: url('https://st.depositphotos.com/2890321/51451/i/600/depositphotos_514519944-stock-photo-close-calendar-purple-table-background.jpg');
            background-size: cover;
            background-position: center;
        }

        /* Optional: semi-transparent overlay for content readability */
        .main > div {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 1rem;
            border-radius: 12px;
        }

        /* Styling sidebar links */
        .sidebar-links img {
            width: 20px;
            margin-right: 10px;
            vertical-align: middle;
        }
        .sidebar-links a {
            text-decoration: none;
            display: inline-block;
            color: white;
            font-weight: bold;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.title("📅 Dynamic Calendar & Task Logger")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose an Option", ("Log Tasks", "View Tasks", "Download Task Data"))

    # Connect with Me Section
    st.sidebar.markdown("## 👨‍💻 Connect with Me")
    st.sidebar.markdown("""
    <div class="sidebar-links">
        <a href="https://github.com/marianadeem755" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png"> GitHub
        </a><br>
        <a href="https://www.kaggle.com/marianadeem755" target="_blank">
            <img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/189_Kaggle_logo_logos-512.png"> Kaggle
        </a><br>
        <a href="mailto:marianadeem755@gmail.com">
            <img src="https://cdn-icons-png.flaticon.com/512/561/561127.png"> Email
        </a><br>
        <a href="https://huggingface.co/maria355" target="_blank">
            <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg"> Hugging Face
        </a>
    </div>
    """, unsafe_allow_html=True)

    if "initialized" not in st.session_state:
        st.session_state.initialized = True

    today = datetime.today()
    month = st.selectbox("Select Month", list(range(1, 13)), index=today.month - 1)
    year = st.selectbox("Select Year", list(range(today.year - 5, today.year + 6)), index=5)

    calendar_df = render_calendar(month, year)
    today_day = highlight_today(month, year)

    for col in calendar_df.columns:
        calendar_df[col] = calendar_df[col].apply(lambda x: f"**{x}**" if x == today_day else x)

    st.table(calendar_df)

    selected_date = st.date_input("Select a Date to Add Tasks", today)

    if app_mode == "Log Tasks":
        log_task_for_date(str(selected_date))

    elif app_mode == "View Tasks":
        view_tasks_by_date()

    elif app_mode == "Download Task Data":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "Download for Day 📅",
                data=get_task_csv("day", str(selected_date)),
                file_name=f"tasks_day_{selected_date}.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                "Download for Month 🗓️",
                data=get_task_csv("month", str(selected_date)),
                file_name=f"tasks_month_{selected_date.strftime('%Y-%m')}.csv",
                mime="text/csv"
            )
        with col3:
            st.download_button(
                "Download for Year 📆",
                data=get_task_csv("year", str(selected_date)),
                file_name=f"tasks_year_{selected_date.strftime('%Y')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()