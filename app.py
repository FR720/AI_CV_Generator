import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from io import BytesIO

from app import main


# Load environment variables
load_dotenv()

# Get API key from environment variable
DEFAULT_API_KEY = os.getenv('GOOGLE_API_KEY')

def verify_api_key(api_key: str) -> bool:
    """Verify that the API key works"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content("Test connection")
        return True
    except Exception as e:
        st.error(f"API Key Error: {str(e)}")
        return False

class CVGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_cv(self, user_data: dict, job_position: str) -> str:
        try:
            prompt = f"""
            Create a professional CV in the following format:

            # {user_data['name']}
            {user_data['email']} | {user_data['phone']}

            ## Professional Summary
            Create a brief professional summary highlighting key strengths and relevance for the {job_position} position.

            ## Professional Experience
            {user_data['experience']}

            ## Education
            {user_data['education']}

            ## Skills
            {user_data['skills']}

            Please ensure:
            1. Use clear markdown formatting
            2. Use bullet points (- ) for listing items
            3. Highlight key achievements and responsibilities
            4. Make content relevant to {job_position} position
            5. Use professional language
            6. Include dates for experience and education
            7. Organize skills in categories if applicable
            """

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating CV: {str(e)}"

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(15, 15, 15)  # Left, Top, Right margins
        self.set_font('Arial', '', 10)  # Set default font
        
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_name_header(self, name, contact):
        self.set_font('Arial', 'B', 16)
        self.multi_cell(0, 10, name, align='C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, contact, align='C')
        self.ln(5)

    def add_section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.multi_cell(0, 10, title)
        self.line(15, self.get_y(), self.get_page_width()-15, self.get_y())
        self.ln(5)

    def add_content(self, text):
        self.set_font('Arial', '', 10)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('- ') or line.startswith('• '):
                    # Handle bullet points
                    self.cell(5, 5, '•', 0, 0)
                    self.multi_cell(0, 5, line[2:].strip())
                    self.ln(2)
                else:
                    # Regular text
                    self.multi_cell(0, 5, line)
                    self.ln(2)

def clean_text_for_pdf(text: str) -> str:
    """Clean and prepare text for PDF generation"""
    # Replace problematic characters
    replacements = {
        '•': '-',
        '–': '-',
        '—': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any non-ASCII characters
    text = ''.join(char for char in text if ord(char) < 128)
    
    return text

def create_cv_pdf(user_data: dict, content: str) -> bytes:
    try:
        # Create BytesIO buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=30
        ))
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12
        ))
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))

        # Build the document content
        story = []

        # Add name and contact info
        story.append(Paragraph(user_data['name'], styles['CustomTitle']))
        story.append(Paragraph(
            f"{user_data['email']} | {user_data['phone']}", 
            styles['CustomBody']
        ))
        story.append(Spacer(1, 12))

        # Process content sections
        sections = content.split('\n## ')
        
        for section in sections:
            if section.strip():
                # Split into title and content
                parts = section.strip().split('\n', 1)
                
                if len(parts) > 1:
                    title, content = parts
                    
                    # Clean the title
                    title = title.replace('#', '').strip()
                    
                    # Add section title
                    story.append(Paragraph(title, styles['CustomHeading']))
                    
                    # Process content
                    for line in content.strip().split('\n'):
                        line = line.strip()
                        if line:
                            if line.startswith('- ') or line.startswith('• '):
                                # Bullet point
                                text = line[2:].strip()
                                bullet = ListFlowable(
                                    [Paragraph(text, styles['CustomBody'])],
                                    bulletType='bullet',
                                    start='•'
                                )
                                story.append(bullet)
                            else:
                                # Regular paragraph
                                story.append(Paragraph(line, styles['CustomBody']))
                    
                    story.append(Spacer(1, 12))

        # Build the PDF
        doc.build(story)
        
        # Get the value from the BytesIO buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        return None
def show_cv_format_guide():
    st.sidebar.markdown("""
    ### CV Format Guide
    
    Your CV will be formatted as follows:
    
    ```markdown
    # Your Name
    email@example.com | Phone Number
    
    ## Professional Summary
    Brief overview of your professional profile
    
    ## Professional Experience
    - Company Name (Date - Date)
      Position Title
      • Key responsibility or achievement
      • Another key responsibility
    
    ## Education
    - Degree Name (Year)
      Institution Name
      • Relevant details or achievements
    
    ## Skills
    - Technical Skills: List of skills
    - Soft Skills: List of skills
    - Other Skills: List of skills
    ```
    """)

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI CV Generator",
        page_icon="📄",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            margin-top: 1rem;
        }
        .success-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            color: #155724;
            margin: 1rem 0;
        }
        .download-section {
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .stMarkdown {
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title with emoji
    st.title("📄 AI-Powered CV Generator")
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration in case you evaluate and api code was expired")
        
        # Use environment variable if available
        api_key = st.text_input(
            "Enter your Google API Key",
            value=DEFAULT_API_KEY if DEFAULT_API_KEY else "",
            type="password"
        )
        
        if api_key:
            if verify_api_key(api_key):
                st.success("✅ API Key verified successfully!")
                if st.checkbox("Show CV Format Guide"):
                    show_cv_format_guide()
            else:
                st.error("❌ Invalid API Key")
                return
        else:
            st.info("""
            ### How to get your API key:
            1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy and paste the key here
            
            Or set GOOGLE_API_KEY in your .env file
            """)
            return

    # Main content
    if api_key:
        # Input form
        with st.form("cv_form"):
            st.subheader("📝 Personal Information")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                name = st.text_input("Full Name")
            with col2:
                email = st.text_input("Email Address")
            with col3:
                phone = st.text_input("Phone Number")
            
            job_position = st.text_input("Target Job Position")
            
            st.subheader("💼 Professional Experience")
            experience = st.text_area(
                "Enter your professional experience",
                height=150,
                help="List your work experience with dates, company names, and key achievements"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🎓 Education")
                education = st.text_area(
                    "Enter your educational background",
                    height=100,
                    help="List your degrees, institutions, and graduation dates"
                )
            
            with col2:
                st.subheader("🔧 Skills")
                skills = st.text_area(
                    "Enter your skills",
                    height=100,
                    help="List relevant technical skills, soft skills, and certifications"
                )
            
            submitted = st.form_submit_button("Generate CV")

        # Handle form submission
        if submitted:
            if not all([name, email, phone, experience, education, skills, job_position]):
                st.error("⚠️ Please fill in all fields")
                return

            try:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "experience": experience,
                    "education": education,
                    "skills": skills
                }
                
                with st.spinner("🔄 Generating CV... This may take a moment."):
                    cv_generator = CVGenerator(api_key)
                    result = cv_generator.generate_cv(user_data, job_position)
                
                if result.startswith("Error"):
                    st.error(result)
                else:
                    st.success("✨ CV Generated Successfully!")
                    
                    # Create tabs for different views
                    tab1, tab2 = st.tabs(["📄 Preview", "⬇️ Download"])
                    
                    with tab1:
                        st.markdown(result)
                    
                    with tab2:
                        st.markdown("### Download Options")
                        
                        try:
                            # Generate PDF
                            pdf_data = create_cv_pdf(user_data, result)
                            
                            if pdf_data:
                                # Download buttons
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.download_button(
                                        label="📥 Download CV as PDF",
                                        data=pdf_data,
                                        file_name=f"cv_{name.lower().replace(' ', '_')}.pdf",
                                        mime="application/pdf",
                                    )
                                
                                with col2:
                                    st.download_button(
                                        label="📄 Download CV as Markdown",
                                        data=result,
                                        file_name=f"cv_{name.lower().replace(' ', '_')}.md",
                                        mime="text/markdown",
                                    )
                            else:
                                st.warning("PDF generation failed. Download as Markdown instead.")
                                st.download_button(
                                    label="📄 Download CV as Markdown",
                                    data=result,
                                    file_name=f"cv_{name.lower().replace(' ', '_')}.md",
                                    mime="text/markdown",
                                )
                            
                            # Copy to clipboard button
                            if st.button("📋 Copy to Clipboard"):
                                st.code(result)
                                st.success("CV content copied to clipboard!")
                                
                        except Exception as e:
                            st.error(f"Error creating PDF: {str(e)}")
                            # Fallback to markdown download
                            st.download_button(
                                label="📄 Download CV as Markdown",
                                data=result,
                                file_name=f"cv_{name.lower().replace(' ', '_')}.md",
                                mime="text/markdown",
                            )
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

 

if __name__ == "__main__":
    main()