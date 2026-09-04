import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Task Manager", page_icon="🤖")
st.title("🤖 AI Project Assistant")

if "token" not in st.session_state:
    st.session_state.token = None
if "project_id" not in st.session_state:
    st.session_state.project_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json().get("access_token")
            st.success("Successfully logged in!")
        else:
            st.error("Login failed. Check your credentials.")

    st.divider()

    if st.session_state.token:
        st.header("📂 Workspace")
        project_id = st.text_input("Enter Project ID", value="1")
        if st.button("Set Project"):
            st.session_state.project_id = project_id
            st.success(f"Active Project: {project_id}")


if st.session_state.token and st.session_state.project_id:
    
    st.markdown("### 📋 Task List")
    
    search_query = st.text_input(
        "🔍 Semantic search:", 
        placeholder="e.g. 'user interface', 'security issues' or 'database'"
    )
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if search_query:
        tasks_res = requests.get(
            f"{API_URL}/projects/{st.session_state.project_id}/tasks/search", 
            headers=headers,
            params={"q": search_query}
        )
    else:
        tasks_res = requests.get(
            f"{API_URL}/projects/{st.session_state.project_id}/tasks/", 
            headers=headers
        )

    if tasks_res.status_code == 200:
        tasks = tasks_res.json()

        if not tasks:
            st.info("No tasks found. Ask the Agent to generate a plan!")
        else:
            for task in tasks:
                col1, col2, col3 = st.columns([0.05, 0.85, 0.1])

                with col1:
                    is_checked = st.checkbox(" ", value=task["is_done"], key=f"task_{task['id']}")
                    if is_checked != task["is_done"]:
                        requests.patch(
                            f"{API_URL}/projects/{st.session_state.project_id}/tasks/{task['id']}/toggle",
                            headers=headers
                        )
                        st.rerun()

                with col2:
                    with st.expander(task["title"] if not task["is_done"] else f"~~{task['title']}~~"):
                        new_title = st.text_input("Edit title", value=task["title"], key=f"title_{task['id']}")
                        new_desc = st.text_area("Edit description", value=task.get("description") or "", key=f"desc_{task['id']}")
                        
                        if st.button("Save changes", key=f"save_{task['id']}"):
                            res = requests.patch(
                                f"{API_URL}/projects/{st.session_state.project_id}/tasks/{task['id']}/update",
                                headers=headers,
                                json={"title": new_title, "description": new_desc}
                            )
                            if res.status_code == 200:
                                st.success("Updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update task.")

                with col3:
                    if st.button("🗑️", key=f"delete_{task['id']}"):
                        del_res = requests.delete(
                            f"{API_URL}/projects/{st.session_state.project_id}/tasks/{task['id']}",
                            headers=headers
                        )
                        if del_res.status_code == 204:
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete task.")

    else:
        st.error("Failed to fetch tasks from the server.")
        
    st.markdown("---")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What should I do (e.g., 'Plan a release cycle for the new app')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                payload = {"text": prompt}

                res = requests.post(
                    f"{API_URL}/projects/{st.session_state.project_id}/tasks/generate",
                    headers=headers,
                    json=payload
                )

                if res.status_code == 200:
                    new_tasks = res.json()
                    response_text = f"Successfully created {len(new_tasks)} new tasks in the database!"
                    st.markdown(response_text)
                    st.json(new_tasks)
                else:
                    response_text = f"An error occurred: {res.text}"
                    st.error(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

else:
    st.info("Please log in and set a Project ID in the sidebar to start chatting with the AI.")