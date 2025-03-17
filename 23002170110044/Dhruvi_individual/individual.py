import mysql.connector
from datetime import datetime, timedelta
from getpass import getpass
from tabulate import tabulate
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import time

console = Console()

# Database setup
def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        assigned_to VARCHAR(50),
                        due_date DATE,
                        status VARCHAR(50) DEFAULT 'Pending',
                        milestone VARCHAR(255),
                        priority VARCHAR(50) DEFAULT 'Normal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id INT,
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS task_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id INT,
                        change_type VARCHAR(50),
                        old_value TEXT,
                        new_value TEXT,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                    )''')
    conn.commit()
    conn.close()

# User authentication
def register_user(username, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (username, password) 
                          VALUES (%s, %s)''', (username, password))
        conn.commit()
        console.print(":white_check_mark: [bold green]User registered successfully![/bold green]")
    except mysql.connector.errors.IntegrityError:
        console.print(":x: [bold red]Username already exists.[/bold red]")
    finally:
        conn.close()

def login_user(username, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Add a new task
def add_task(title, description, assigned_to, due_date, milestone, priority):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tasks (title, description, assigned_to, due_date, milestone, priority) 
                      VALUES (%s, %s, %s, %s, %s, %s)''', 
                   (title, description, assigned_to, due_date, milestone, priority))
    task_id = cursor.lastrowid
    cursor.execute('''INSERT INTO task_history (task_id, change_type, old_value, new_value) 
                      VALUES (%s, %s, %s, %s)''', 
                   (task_id, "Task Created", "", title))
    conn.commit()
    conn.close()
    console.print(":white_check_mark: [bold green]Task added successfully![/bold green] :memo:")

# View all tasks
def view_tasks():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id")
    tasks = cursor.fetchall()
    conn.close()
    if tasks and len(tasks) > 0:
        table = Table(title="All Tasks", box=box.ROUNDED, show_lines=True)
        headers = ["Serial No.", "Title", "Description", "Assigned To", "Due Date", "Status", "Milestone", "Priority", "Created At"]
        for header in headers:
            table.add_column(header, style="bold cyan")
        for i, task in enumerate(tasks):
            table.add_row(str(i+1), *map(str, task[1:]))
        console.print(table)
    else:
        console.print(":x: [bold red]No tasks found.[/bold red] :mag:")

# View tasks by milestone
def view_tasks_by_milestone(milestone):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE milestone = %s", (milestone,))
    tasks = cursor.fetchall()
    conn.close()
    if tasks and len(tasks) > 0:
        table = Table(title=f"Tasks for Milestone '{milestone}'", box=box.ROUNDED, show_lines=True)
        headers = ["Serial No.", "Title", "Description", "Assigned To", "Due Date", "Status", "Milestone", "Priority", "Created At"]
        for header in headers:
            table.add_column(header, style="bold cyan")
        for i, task in enumerate(tasks):
            table.add_row(str(i+1), *map(str, task[1:]))
        console.print(table)
    else:
        console.print(f":x: [bold red]No tasks found for Milestone '{milestone}'.[/bold red] :mountain:")

# Update task status
def update_task_status(serial_no, status):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task = cursor.fetchone()
    if task:
        task_id, old_status = task[0], task[1]
        cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
        cursor.execute('''INSERT INTO task_history (task_id, change_type, old_value, new_value) 
                          VALUES (%s, %s, %s, %s)''', 
                       (task_id, "Status Changed", old_status, status))
        conn.commit()
        console.print(":white_check_mark: [bold green]Task status updated successfully![/bold green] :chart_with_upwards_trend:")
    conn.close()

# Update task priority
def update_task_priority(serial_no, priority):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, priority FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task = cursor.fetchone()
    if task:
        task_id, old_priority = task[0], task[1]
        cursor.execute("UPDATE tasks SET priority = %s WHERE id = %s", (priority, task_id))
        cursor.execute('''INSERT INTO task_history (task_id, change_type, old_value, new_value) 
                          VALUES (%s, %s, %s, %s)''', 
                       (task_id, "Priority Changed", old_priority, priority))
        conn.commit()
        console.print(":white_check_mark: [bold green]Task priority updated successfully![/bold green] :arrow_up:")
    conn.close()

# Add a comment to a task
def add_comment(serial_no, comment):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task = cursor.fetchone()
    if task:
        task_id = task[0]
        cursor.execute("INSERT INTO comments (task_id, comment) VALUES (%s, %s)", (task_id, comment))
        conn.commit()
        console.print(":white_check_mark: [bold green]Comment added successfully![/bold green] :speech_balloon:")
    conn.close()

# Delete a task
def delete_task(serial_no):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task = cursor.fetchone()
    if task:
        task_id = task[0]
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("ALTER TABLE tasks AUTO_INCREMENT = 1")
            conn.commit()
        console.print(":white_check_mark: [bold green]Task deleted successfully![/bold green] :wastebasket:")
    conn.close()

# View comments for a task   
def view_comments(serial_no):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task = cursor.fetchone()
    if task:
        task_id = task[0]
        cursor.execute("SELECT * FROM comments WHERE task_id = %s", (task_id,))
        comments = cursor.fetchall()
        conn.close()

        if comments:
            table = Table(title=f"Comments for Task Serial No. {serial_no}", box=box.ROUNDED, show_lines=True)
            headers = ["ID", "Task ID", "Comment", "Created At"]
            for header in headers:
                table.add_column(header, style="bold cyan")
            for comment in comments:
                table.add_row(*map(str, comment))
            console.print(table)
        else:
            console.print(":x: [bold red]No comments found for this task.[/bold red] :speech_balloon:")
    else:
        conn.close()
        console.print(f":x: [bold red]No task found for serial number {serial_no}.[/bold red] :mag:")

# View task history
def view_task_history(serial_no):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks ORDER BY id LIMIT %s, 1", (serial_no - 1,))
    task_id = cursor.fetchone()[0]
    cursor.execute("SELECT change_type, old_value, new_value, changed_at FROM task_history WHERE task_id = %s", (task_id,))
    history = cursor.fetchall()
    conn.close()

    if history:
        table = Table(title=f"History for Task Serial No. {serial_no}", box=box.ROUNDED, show_lines=True)
        headers = ["Serial No.", "Change Type", "Old Value", "New Value", "Changed At"]
        for header in headers:
            table.add_column(header, style="bold cyan")
        for i, record in enumerate(history):
            table.add_row(str(i+1), *map(str, record))
        console.print(table)
    else:
        console.print(":x: [bold red]No history found for this task.[/bold red] :clock1:")

# Analyze tasks using Matplotlib
def analyze_tasks():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    
    # Task status analysis
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    status_data = cursor.fetchall()
    statuses, status_counts = zip(*status_data) if status_data else ([], [])

    # Priority analysis
    cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    priority_data = cursor.fetchall()
    priorities, priority_counts = zip(*priority_data) if priority_data else ([], [])

    # Milestone analysis
    cursor.execute("SELECT milestone, COUNT(*) FROM tasks GROUP BY milestone")
    milestone_data = cursor.fetchall()
    milestones, milestone_counts = zip(*milestone_data) if milestone_data else ([], [])

    conn.close()

    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    # Task status pie chart
    axs[0].pie(status_counts, labels=statuses, autopct="%1.1f%%", colors=["blue", "orange", "green"])
    axs[0].set_title("Task Status Distribution")

    # Priority bar chart
    axs[1].bar(priorities, priority_counts, color=["red", "blue", "green"])
    axs[1].set_title("Task Priority Distribution")
    axs[1].set_xlabel("Priority")
    axs[1].set_ylabel("Count")

    # Milestone bar chart
    axs[2].bar(milestones, milestone_counts, color="purple")
    axs[2].set_title("Tasks per Milestone")
    axs[2].set_xlabel("Milestone")
    axs[2].set_ylabel("Count")

    plt.tight_layout()
    plt.show()

# Search tasks by title, description, or assigned user
def search_tasks(keyword):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    query = '''SELECT * FROM tasks WHERE 
               title LIKE %s OR 
               description LIKE %s OR 
               assigned_to LIKE %s'''
    like_keyword = f"%{keyword}%"
    cursor.execute(query, (like_keyword, like_keyword, like_keyword))
    tasks = cursor.fetchall()
    conn.close()
    if tasks and len(tasks) > 0:
        table = Table(title=f"Search Results for '{keyword}'", box=box.ROUNDED, show_lines=True)
        headers = ["ID", "Title", "Description", "Assigned To", "Due Date", "Status", "Milestone", "Priority", "Created At"]
        for header in headers:
            table.add_column(header, style="bold cyan")
        for task in tasks:
            table.add_row(*map(str, task))
        console.print(table)
    else:
        console.print(f":x: [bold red]No tasks found for keyword '{keyword}'.[/bold red] :mag:")

# Task reminders for tasks nearing their due date
def task_reminders():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="task"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT title, due_date FROM tasks WHERE due_date <= %s AND status != 'Completed'", (datetime.now() + timedelta(days=2),))
    tasks = cursor.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            title, due_date = task
            console.print(f":alarm_clock: [bold yellow]Reminder:[/bold yellow] Task '{title}' is due on {due_date}.")
    else:
        console.print(":white_check_mark: [bold green]No tasks are nearing their due date.[/bold green]")

# CLI interface
def main():
    init_db()
    console.print(Panel(":wave: [bold blue]Welcome to the Collaborative Task Management System[/bold blue]", title="Task Management", subtitle="Manage your tasks efficiently", box=box.DOUBLE))

    logged_in_user = None

    while True:
        if not logged_in_user:
            console.print(Panel("\n:lock: [bold yellow]Authentication:[/bold yellow]\n1. Register :key:\n2. Login :unlock:\n3. Exit :door:", title="Authentication", box=box.ROUNDED))

            choice = input("Enter your choice: ")

            if choice == '1':
                username = input("Username: ")
                password = getpass("Password: ")
                register_user(username, password)

            elif choice == '2':
                username = input("Username: ")
                password = getpass("Password: ")
                user = login_user(username, password)
                if user:
                    logged_in_user = user
                    console.print(f":white_check_mark: [bold green]Welcome, {username}![/bold green]")
                else:
                    console.print(":x: [bold red]Invalid username or password.[/bold red]")

            elif choice == '3':
                console.print(":wave: [bold blue]Exiting... Goodbye![/bold blue]")
                break

            else:
                console.print(":x: [bold red]Invalid choice. Please try again.[/bold red]")

        else:
            console.print(Panel("\n:gear: [bold yellow]Options:[/bold yellow]\n1. Add Task :memo:\n2. View All Tasks :mag:\n3. View Tasks by Milestone :mountain:\n4. View Comments for a Task :speech_balloon:\n5. Update Task Status :chart_with_upwards_trend:\n6. Update Task Priority :arrow_up:\n7. Add Comment to Task :speech_balloon:\n8. Delete Task :wastebasket:\n9. Analyze Tasks :bar_chart:\n10. Search Tasks :mag:\n11. View Task History :clock1:\n12. Task Reminders :alarm_clock:\n13. Logout :door:", title="Options", box=box.ROUNDED))

            choice = input("Enter your choice: ")

            if choice == '1':
                title = input("Task Title: ")
                description = input("Task Description: ")
                assigned_to = input("Assigned To: ")
                due_date = input("Due Date (YYYY-MM-DD): ")
                milestone = input("Milestone: ")
                priority = input("Priority (Low/Normal/High): ")
                add_task(title, description, assigned_to, due_date, milestone, priority)

            elif choice == '2':
                view_tasks()

            elif choice == '3':
                milestone = input("Enter Milestone: ")
                view_tasks_by_milestone(milestone)

            elif choice == '4':
                serial_no = int(input("Enter Task Serial Number: "))
                view_comments(serial_no)

            elif choice == '5':
                serial_no = int(input("Enter Task Serial Number to update: "))
                status = input("Enter new status (Pending/In Progress/Completed): ")
                update_task_status(serial_no, status)

            elif choice == '6':
                serial_no = int(input("Enter Task Serial Number to update: "))
                priority = input("Enter new priority (Low/Normal/High): ")
                update_task_priority(serial_no, priority)

            elif choice == '7':
                serial_no = int(input("Enter Task Serial Number: "))
                comment = input("Enter your comment: ")
                add_comment(serial_no, comment)

            elif choice == '8':
                serial_no = int(input("Enter Task Serial Number to delete: "))
                delete_task(serial_no)

            elif choice == '9':
                analyze_tasks()

            elif choice == '10':
                keyword = input("Enter title, description, or assigned user to search tasks: ")
                search_tasks(keyword)

            elif choice == '11':
                serial_no = int(input("Enter Task Serial Number to view history: "))
                view_task_history(serial_no)

            elif choice == '12':
                task_reminders()

            elif choice == '13':
                logged_in_user = None
                console.print(":wave: [bold blue]Logged out successfully.[/bold blue]")

            else:
                console.print(":x: [bold red]Invalid choice. Please try again.[/bold red]")

if __name__ == "__main__":
    main()