import streamlit as st
import pandas as pd
from datetime import datetime
import json
from database import Database
from llm_service import LLMService
from load_mock_data import load_mock_emails

# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
    load_mock_emails()  # Load mock data if not already loaded

if 'llm' not in st.session_state:
    try:
        st.session_state.llm = LLMService()
        st.session_state.llm_ready = True
    except ValueError as e:
        st.session_state.llm_ready = False
        st.error(f"⚠️ {str(e)}")

if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS
st.markdown("""
<style>
    .email-card {
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .email-header {
        font-weight: bold;
        color: #1f77b4;
    }
    .category-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .category-important {
        background-color: #ff4444;
        color: white;
    }
    .category-todo {
        background-color: #ff9800;
        color: white;
    }
    .category-newsletter {
        background-color: #2196F3;
        color: white;
    }
    .category-spam {
        background-color: #666666;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📧 Email Productivity Agent")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📥 Inbox", "🤖 Email Agent Chat", "✍️ Draft Generator", "⚙️ Prompt Configuration"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "An intelligent email productivity agent powered by Gemini AI. "
    "Categorize emails, extract action items, generate drafts, and interact with your inbox using natural language."
)

# ===== PAGE 1: INBOX =====
if page == "📥 Inbox":
    st.title("📥 Email Inbox")
    
    if not st.session_state.llm_ready:
        st.error("LLM service is not ready. Please check your GEMINI_API_KEY in the .env file.")
        st.stop()
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        if st.button("🔄 Refresh Inbox"):
            st.rerun()
    
    with col2:
        process_all = st.button("⚡ Process All Emails")
    
    # Get all emails
    emails = st.session_state.db.get_all_emails()
    
    if process_all:
        with st.spinner("Processing all emails..."):
            prompt_data = st.session_state.db.get_prompt_by_type("categorization")
            action_prompt_data = st.session_state.db.get_prompt_by_type("action_extraction")
            
            if prompt_data and action_prompt_data:
                categorization_template = prompt_data[3]
                action_template = action_prompt_data[3]
                
                progress_bar = st.progress(0)
                for idx, email in enumerate(emails):
                    email_id, sender, subject, body, timestamp, category, action_items, processed = email
                    
                    # Categorize
                    category = st.session_state.llm.categorize_email(
                        sender, subject, body, categorization_template
                    )
                    st.session_state.db.update_email_category(email_id, category)
                    
                    # Extract actions if To-Do
                    if "to-do" in category.lower():
                        actions = st.session_state.llm.extract_action_items(
                            sender, subject, body, action_template
                        )
                        st.session_state.db.update_email_actions(email_id, actions)
                    
                    progress_bar.progress((idx + 1) / len(emails))
                
                st.success("✅ All emails processed successfully!")
                st.rerun()
    
    # Filter options
    st.markdown("### Filter Emails")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        category_filter = st.multiselect(
            "Filter by Category",
            ["Important", "To-Do", "Newsletter", "Spam"],
            default=[]
        )
    
    with filter_col2:
        show_processed = st.checkbox("Show only processed emails", value=False)
    
    # Display emails
    st.markdown("---")
    st.markdown("### Emails")
    
    filtered_emails = emails
    if category_filter:
        filtered_emails = [e for e in filtered_emails if e[5] in category_filter]
    if show_processed:
        filtered_emails = [e for e in filtered_emails if e[7] == 1]
    
    if not filtered_emails:
        st.info("No emails found matching the filter criteria.")
    
    for email in filtered_emails:
        email_id, sender, subject, body, timestamp, category, action_items, processed = email
        
        with st.expander(f"📧 **{subject}** - From: {sender}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**From:** {sender}")
                st.markdown(f"**Subject:** {subject}")
                st.markdown(f"**Date:** {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')}")
                
                if category:
                    category_class = f"category-{category.lower()}"
                    st.markdown(
                        f'<span class="category-badge {category_class}">{category}</span>',
                        unsafe_allow_html=True
                    )
            
            with col2:
                if st.button("🔄 Process", key=f"process_{email_id}"):
                    with st.spinner("Processing..."):
                        # Categorize
                        prompt_data = st.session_state.db.get_prompt_by_type("categorization")
                        if prompt_data:
                            category = st.session_state.llm.categorize_email(
                                sender, subject, body, prompt_data[3]
                            )
                            st.session_state.db.update_email_category(email_id, category)
                            st.success(f"Categorized as: {category}")
                            
                            # Extract actions if To-Do
                            if "to-do" in category.lower():
                                action_prompt = st.session_state.db.get_prompt_by_type("action_extraction")
                                if action_prompt:
                                    actions = st.session_state.llm.extract_action_items(
                                        sender, subject, body, action_prompt[3]
                                    )
                                    st.session_state.db.update_email_actions(email_id, actions)
                            
                            st.rerun()
                
                if st.button("✍️ Draft Reply", key=f"draft_{email_id}"):
                    st.session_state.selected_email_id = email_id
                    st.switch_page = "✍️ Draft Generator"
                    st.info("Switch to 'Draft Generator' tab to see the draft")
            
            st.markdown("**Email Body:**")
            st.text_area("", value=body, height=150, key=f"body_{email_id}", disabled=True)
            
            # Show action items if available
            if action_items:
                try:
                    actions = json.loads(action_items)
                    if actions.get("tasks"):
                        st.markdown("**📋 Action Items:**")
                        for task in actions["tasks"]:
                            task_text = task.get("task", "")
                            deadline = task.get("deadline", "No deadline")
                            st.markdown(f"- {task_text} *(Deadline: {deadline})*")
                except:
                    pass

# ===== PAGE 2: EMAIL AGENT CHAT =====
elif page == "🤖 Email Agent Chat":
    st.title("🤖 Email Agent Chat")
    
    if not st.session_state.llm_ready:
        st.error("LLM service is not ready. Please check your GEMINI_API_KEY in the .env file.")
        st.stop()
    
    st.markdown("""
    Ask questions about your emails or request actions. For example:
    - "Summarize this email from john.smith@company.com"
    - "Show me all urgent emails"
    - "What tasks do I need to do?"
    - "Draft a reply based on my tone"
    """)
    
    # Email selection for context
    st.markdown("---")
    st.markdown("### Select Email for Context (Optional)")
    
    emails = st.session_state.db.get_all_emails()
    email_options = {f"{e[2]} - {e[1]}": e[0] for e in emails}
    
    selected_email_subject = st.selectbox(
        "Choose an email to provide context",
        ["None"] + list(email_options.keys())
    )
    
    # Chat interface
    st.markdown("---")
    st.markdown("### Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your emails...")
    
    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Prepare context
        email_context = ""
        if selected_email_subject != "None":
            email_id = email_options[selected_email_subject]
            email = st.session_state.db.get_email_by_id(email_id)
            if email:
                email_context = f"""
Selected Email:
From: {email[1]}
Subject: {email[2]}
Body: {email[3]}
Category: {email[5] if email[5] else 'Not categorized'}
"""
        else:
            # Provide general inbox context
            all_emails = st.session_state.db.get_all_emails()
            email_context = f"Total emails in inbox: {len(all_emails)}\n\n"
            
            # Group by category
            categories = {}
            for e in all_emails:
                cat = e[5] if e[5] else "Uncategorized"
                categories[cat] = categories.get(cat, 0) + 1
            
            email_context += "Email breakdown by category:\n"
            for cat, count in categories.items():
                email_context += f"- {cat}: {count}\n"
        
        # Get prompts info
        prompts = st.session_state.db.get_all_prompts()
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.llm.chat_with_agent(
                    user_input, email_context, prompts
                )
                st.markdown(response)
        
        # Add assistant response to chat
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# ===== PAGE 3: DRAFT GENERATOR =====
elif page == "✍️ Draft Generator":
    st.title("✍️ Email Draft Generator")
    
    if not st.session_state.llm_ready:
        st.error("LLM service is not ready. Please check your GEMINI_API_KEY in the .env file.")
        st.stop()
    
    # Email selection
    st.markdown("### Select Email to Reply To")
    
    emails = st.session_state.db.get_all_emails()
    email_options = {f"{e[2]} - From: {e[1]}": e[0] for e in emails}
    
    selected_email_subject = st.selectbox(
        "Choose an email",
        list(email_options.keys()),
        index=0
    )
    
    email_id = email_options[selected_email_subject]
    email = st.session_state.db.get_email_by_id(email_id)
    
    if email:
        # Display original email
        st.markdown("---")
        st.markdown("### Original Email")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**From:** {email[1]}")
            st.markdown(f"**Subject:** {email[2]}")
        with col2:
            st.markdown(f"**Date:** {datetime.fromisoformat(email[4]).strftime('%Y-%m-%d %H:%M')}")
            if email[5]:
                st.markdown(f"**Category:** {email[5]}")
        
        st.text_area("Original Message", value=email[3], height=200, disabled=True)
        
        # Draft generation
        st.markdown("---")
        st.markdown("### Generate Draft")
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="E.g., 'I'm available on Thursday afternoon' or 'Keep the tone formal'",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            generate_draft = st.button("✨ Generate Draft", type="primary")
        
        if generate_draft:
            with st.spinner("Generating draft..."):
                prompt_data = st.session_state.db.get_prompt_by_type("auto_reply")
                if prompt_data:
                    draft = st.session_state.llm.generate_reply(
                        email[1], email[2], email[3],
                        prompt_data[3],
                        additional_context
                    )
                    
                    st.session_state.current_draft = draft
                    st.rerun()
        
        # Display and edit draft
        if 'current_draft' in st.session_state and st.session_state.current_draft:
            st.markdown("---")
            st.markdown("### Generated Draft")
            
            edited_draft = st.text_area(
                "Edit the draft as needed",
                value=st.session_state.current_draft,
                height=300,
                key="draft_editor"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            
            with col1:
                if st.button("💾 Save Draft"):
                    draft_subject = f"Re: {email[2]}"
                    st.session_state.db.save_draft(
                        email_id,
                        draft_subject,
                        edited_draft,
                        {"original_sender": email[1]}
                    )
                    st.success("✅ Draft saved successfully!")
            
            with col2:
                if st.button("🗑️ Discard"):
                    st.session_state.current_draft = None
                    st.rerun()
            
            st.info("📝 Note: Drafts are saved but not sent automatically. This is a safety feature.")
    
    # Show saved drafts
    st.markdown("---")
    st.markdown("### Saved Drafts")
    
    drafts = st.session_state.db.get_drafts()
    
    if not drafts:
        st.info("No saved drafts yet.")
    else:
        for draft in drafts:
            draft_id, email_id, subject, body, metadata, created_at, sender, original_subject = draft
            
            with st.expander(f"📝 {subject} (Created: {created_at})"):
                st.markdown(f"**In reply to:** {original_subject} from {sender}")
                st.markdown(f"**Subject:** {subject}")
                st.text_area("Draft Body", value=body, height=200, key=f"saved_draft_{draft_id}", disabled=True)
                
                if st.button("🗑️ Delete Draft", key=f"delete_draft_{draft_id}"):
                    st.session_state.db.delete_draft(draft_id)
                    st.success("Draft deleted!")
                    st.rerun()

# ===== PAGE 4: PROMPT CONFIGURATION =====
elif page == "⚙️ Prompt Configuration":
    st.title("⚙️ Prompt Configuration")
    
    st.markdown("""
    Configure and customize the AI prompts that power the email agent.
    These prompts guide how emails are categorized, how action items are extracted,
    and how replies are generated.
    """)
    
    # Get all prompts
    prompts = st.session_state.db.get_all_prompts()
    
    st.markdown("---")
    
    # Tabs for different prompt types
    tab1, tab2, tab3, tab4 = st.tabs([
        "📂 Categorization",
        "📋 Action Extraction",
        "✍️ Auto-Reply",
        "➕ Create Custom"
    ])
    
    with tab1:
        st.markdown("### Email Categorization Prompt")
        prompt_data = st.session_state.db.get_prompt_by_type("categorization")
        
        if prompt_data:
            st.markdown(f"**Last Updated:** {prompt_data[5]}")
            
            current_template = prompt_data[3]
            edited_template = st.text_area(
                "Prompt Template",
                value=current_template,
                height=300,
                key="cat_prompt",
                help="Use {sender}, {subject}, and {body} as placeholders"
            )
            
            if st.button("💾 Save Categorization Prompt"):
                st.session_state.db.update_prompt("categorization", edited_template)
                st.success("✅ Prompt updated successfully!")
                st.rerun()
    
    with tab2:
        st.markdown("### Action Item Extraction Prompt")
        prompt_data = st.session_state.db.get_prompt_by_type("action_extraction")
        
        if prompt_data:
            st.markdown(f"**Last Updated:** {prompt_data[5]}")
            
            current_template = prompt_data[3]
            edited_template = st.text_area(
                "Prompt Template",
                value=current_template,
                height=300,
                key="action_prompt",
                help="Use {sender}, {subject}, and {body} as placeholders"
            )
            
            if st.button("💾 Save Action Extraction Prompt"):
                st.session_state.db.update_prompt("action_extraction", edited_template)
                st.success("✅ Prompt updated successfully!")
                st.rerun()
    
    with tab3:
        st.markdown("### Auto-Reply Draft Prompt")
        prompt_data = st.session_state.db.get_prompt_by_type("auto_reply")
        
        if prompt_data:
            st.markdown(f"**Last Updated:** {prompt_data[5]}")
            
            current_template = prompt_data[3]
            edited_template = st.text_area(
                "Prompt Template",
                value=current_template,
                height=300,
                key="reply_prompt",
                help="Use {sender}, {subject}, {body}, and {additional_context} as placeholders"
            )
            
            if st.button("💾 Save Auto-Reply Prompt"):
                st.session_state.db.update_prompt("auto_reply", edited_template)
                st.success("✅ Prompt updated successfully!")
                st.rerun()
    
    with tab4:
        st.markdown("### Create Custom Prompt")
        st.markdown("Create a new custom prompt for specific use cases.")
        
        new_prompt_name = st.text_input("Prompt Name", placeholder="E.g., Meeting Scheduler")
        new_prompt_type = st.text_input("Prompt Type", placeholder="E.g., meeting_scheduler")
        new_prompt_template = st.text_area(
            "Prompt Template",
            height=300,
            placeholder="Enter your custom prompt template here...",
            help="Use {sender}, {subject}, and {body} as placeholders"
        )
        
        if st.button("➕ Create Prompt"):
            if new_prompt_name and new_prompt_type and new_prompt_template:
                try:
                    st.session_state.db.create_prompt(
                        new_prompt_name,
                        new_prompt_type,
                        new_prompt_template
                    )
                    st.success(f"✅ Custom prompt '{new_prompt_name}' created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating prompt: {str(e)}")
            else:
                st.warning("Please fill in all fields.")
    
    # Display all prompts
    st.markdown("---")
    st.markdown("### All Prompts Overview")
    
    prompt_df = pd.DataFrame(
        prompts,
        columns=["ID", "Name", "Type", "Template", "Created", "Updated"]
    )
    prompt_df = prompt_df[["Name", "Type", "Updated"]]
    
    st.dataframe(prompt_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Email Productivity Agent | Powered by Google Gemini AI"
    "</div>",
    unsafe_allow_html=True
)

