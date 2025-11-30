import sqlite3
from datetime import datetime, timedelta
from database import Database
import random

# Mock email data
MOCK_EMAILS = [
    {
        "sender": "john.smith@company.com",
        "subject": "Team Meeting Scheduled for Tomorrow",
        "body": """Hi Team,

I've scheduled our weekly sync for tomorrow at 10 AM. Please review the project status report before the meeting and come prepared with your updates.

Agenda:
1. Sprint review
2. Blockers discussion
3. Next week planning

See you there!

Best regards,
John Smith""",
        "days_ago": 0
    },
    {
        "sender": "newsletter@techdigest.com",
        "subject": "Your Weekly Tech Digest - AI Trends 2025",
        "body": """Hello Subscriber,

Here are this week's top stories in technology:

1. New AI breakthrough in natural language processing
2. Quantum computing reaches new milestone
3. Cybersecurity best practices for 2025

Read more at our website.

Unsubscribe | Manage Preferences""",
        "days_ago": 1
    },
    {
        "sender": "spam@lottery-winner.net",
        "subject": "CONGRATULATIONS! You've Won $1,000,000!!!",
        "body": """Dear Lucky Winner,

You have been selected to receive ONE MILLION DOLLARS! Click here to claim your prize NOW!

This is a limited time offer. Act fast!

Click here: http://suspicious-link.net

Best regards,
International Lottery Commission""",
        "days_ago": 1
    },
    {
        "sender": "sarah.johnson@client.com",
        "subject": "Urgent: Project Deadline Extension Request",
        "body": """Hi,

I hope this email finds you well. I wanted to discuss the current project timeline. Given some unexpected challenges, we need to request a 2-week extension on the deliverables.

Could we schedule a call this week to discuss this? Please let me know your availability for Thursday or Friday.

Thanks,
Sarah Johnson
Project Manager""",
        "days_ago": 0
    },
    {
        "sender": "hr@company.com",
        "subject": "Action Required: Complete Your Annual Performance Review",
        "body": """Dear Employee,

This is a reminder to complete your annual performance review by Friday, December 6th.

Please log into the HR portal and:
1. Complete your self-assessment
2. Set goals for next year
3. Submit the form by EOD Friday

Failure to complete this by the deadline may delay your performance bonus.

Best regards,
Human Resources""",
        "days_ago": 2
    },
    {
        "sender": "marketing@deals.com",
        "subject": "Exclusive Black Friday Deals Inside!",
        "body": """Don't Miss Out!

Up to 70% off on all electronics! 
Limited time offer - ends this weekend!

Shop now: www.deals.com

Unsubscribe | Update Preferences

This email was sent to you because you subscribed to our mailing list.""",
        "days_ago": 3
    },
    {
        "sender": "david.chen@partner.com",
        "subject": "Re: Contract Review - Needs Your Signature",
        "body": """Hi,

Following up on the contract we discussed last week. I've attached the final version with the changes we agreed upon.

Please review and sign by Wednesday so we can move forward with the project kickoff next Monday.

Let me know if you have any questions.

Best,
David Chen""",
        "days_ago": 1
    },
    {
        "sender": "notifications@github.com",
        "subject": "New pull request in your repository",
        "body": """A new pull request has been opened in your repository 'email-agent'.

PR #42: Add email categorization feature
Author: contributor@github.com

View Pull Request: https://github.com/yourrepo/email-agent/pull/42

Reply to this email to comment on the pull request.""",
        "days_ago": 0
    },
    {
        "sender": "mike.brown@company.com",
        "subject": "Quick Question about API Documentation",
        "body": """Hey,

Quick question - where can I find the latest API documentation for the email service? The link in the wiki seems to be broken.

Also, do you have any code examples for implementing the authentication flow?

Thanks!
Mike""",
        "days_ago": 1
    },
    {
        "sender": "events@conference.org",
        "subject": "Reminder: Tech Conference Registration Closes Tomorrow",
        "body": """Dear Attendee,

This is a friendly reminder that registration for the Annual Tech Conference 2025 closes tomorrow at midnight.

Event Details:
- Date: January 15-17, 2025
- Location: Convention Center, San Francisco
- Early bird discount: $200 off

Register now: www.conference.org/register

See you there!
Events Team""",
        "days_ago": 2
    },
    {
        "sender": "lisa.wong@company.com",
        "subject": "Meeting Notes and Action Items from Yesterday",
        "body": """Hi all,

Thanks for joining yesterday's meeting. Here are the key takeaways and action items:

Action Items:
- @John: Update the database schema by next week
- @Sarah: Review the UI mockups and provide feedback by Thursday
- @Mike: Set up the staging environment by Friday

Next meeting: Same time next week.

Best,
Lisa Wong""",
        "days_ago": 1
    },
    {
        "sender": "security@bank-alert.com",
        "subject": "URGENT: Verify Your Account Now",
        "body": """SECURITY ALERT

We detected unusual activity on your account. 

Verify your identity immediately to prevent account suspension.

Click here: http://fake-bank-site.com/verify

You have 24 hours to respond.

Security Team""",
        "days_ago": 0
    },
    {
        "sender": "admin@company.com",
        "subject": "System Maintenance Scheduled - December 5th",
        "body": """Dear Users,

We will be performing scheduled system maintenance on Thursday, December 5th from 2:00 AM to 6:00 AM EST.

During this time:
- Email services will be unavailable
- File storage will be in read-only mode
- Video conferencing will remain operational

Please plan accordingly and save your work before the maintenance window.

Thank you for your patience.

IT Administration""",
        "days_ago": 3
    },
    {
        "sender": "newsletter@productivity.com",
        "subject": "5 Tips to Boost Your Productivity This Week",
        "body": """Hello Productive People!

Here are this week's productivity tips:

1. Use the Pomodoro Technique for focused work
2. Batch similar tasks together
3. Set clear priorities each morning
4. Take regular breaks
5. Use automation tools

Read the full article on our blog.

Unsubscribe | Manage Settings""",
        "days_ago": 4
    },
    {
        "sender": "rachel.green@vendor.com",
        "subject": "Invoice #2024-1156 - Payment Due",
        "body": """Dear Client,

Please find attached Invoice #2024-1156 for the services provided in November.

Amount Due: $5,250.00
Due Date: December 15, 2024

Payment can be made via:
- Bank transfer
- Credit card
- Check

Please confirm receipt of this invoice.

Best regards,
Rachel Green
Accounts Receivable""",
        "days_ago": 5
    },
    {
        "sender": "tom.anderson@company.com",
        "subject": "Great job on the presentation!",
        "body": """Hi,

I just wanted to say great job on yesterday's client presentation! The demo went really smoothly and the client seemed very impressed.

They mentioned they want to move forward with the proposal. I'll set up a follow-up meeting for next week.

Keep up the excellent work!

Tom Anderson
Sales Director""",
        "days_ago": 1
    },
    {
        "sender": "updates@linkedin.com",
        "subject": "You have 3 new connection requests",
        "body": """Hi there,

You have new activity on LinkedIn:

- 3 new connection requests
- 5 people viewed your profile
- 2 new messages

View your notifications: www.linkedin.com/notifications

Best,
The LinkedIn Team

Unsubscribe | Settings""",
        "days_ago": 2
    },
    {
        "sender": "emily.davis@company.com",
        "subject": "Request: Review Design Mockups by EOD",
        "body": """Hey,

I've finished the new design mockups for the dashboard redesign project. Could you please review them and share your feedback by end of day?

The files are in the shared drive: /Projects/Dashboard/Designs/v2

Specifically looking for feedback on:
- Color scheme
- Navigation flow
- Mobile responsiveness

Thanks!
Emily Davis
UX Designer""",
        "days_ago": 0
    },
    {
        "sender": "support@software.com",
        "subject": "Your Support Ticket #78924 has been resolved",
        "body": """Hello,

Your support ticket #78924 regarding 'Login authentication issue' has been resolved.

Resolution: We've reset your authentication token. Please try logging in again with your existing credentials.

If you continue to experience issues, please reply to this email or open a new ticket.

Thank you for your patience.

Support Team""",
        "days_ago": 3
    },
    {
        "sender": "alex.martinez@company.com",
        "subject": "Team Lunch Next Friday - RSVP Needed",
        "body": """Hi Team,

We're organizing a team lunch next Friday at 12:30 PM at the new Italian restaurant downtown.

Please RSVP by Wednesday so I can make a reservation for the right number of people.

Looking forward to seeing everyone there!

Alex Martinez""",
        "days_ago": 4
    }
]

def load_mock_emails():
    """Load mock emails into the database"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if emails already exist
    cursor.execute("SELECT COUNT(*) FROM emails")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Database already contains {count} emails. Skipping mock data load.")
        conn.close()
        return
    
    print("Loading mock email data...")
    
    for email in MOCK_EMAILS:
        timestamp = (datetime.now() - timedelta(days=email["days_ago"])).isoformat()
        cursor.execute("""
            INSERT INTO emails (sender, subject, body, timestamp)
            VALUES (?, ?, ?, ?)
        """, (email["sender"], email["subject"], email["body"], timestamp))
    
    conn.commit()
    conn.close()
    
    print(f"Successfully loaded {len(MOCK_EMAILS)} mock emails into the database.")

if __name__ == "__main__":
    load_mock_emails()

