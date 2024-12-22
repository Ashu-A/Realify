
from pyrevit import forms
import subprocess
import os
from System.Windows.Documents import Run, Paragraph
from System.Windows.Media import Brushes

# Define the function to send a question to ChatGPT
def ask_chatgpt(question):
    try:
        # Run chatgpt_service.py with the user's question as a command-line argument
        result = subprocess.check_output(
            [
                r"....",  # Full path to Python executable
                r"....",  # Full path to chatgpt_service.py
                question
            ],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        return "Error from chatgpt_service.py: " + e.output.strip()
    except Exception as e:
        return "An unexpected error occurred: " + str(e)

# Define the main form class
class ChatGPTForm(forms.WPFWindow):
    def __init__(self):
        # Load the XAML file
        xaml_path = os.path.join(os.path.dirname(__file__), "ChatGPTForm.xaml")
        forms.WPFWindow.__init__(self, xaml_path)

        # Attach the Send button click event
        self.SendButton.Click += self.send_button_click

    def send_button_click(self, sender, args):
        # Get the user's question from the QuestionInput TextBox
        user_question = self.QuestionInput.Text.strip()
        if user_question == "":
            return

        # Add the user's question in red to the ConversationHistory RichTextBox
        user_paragraph = Paragraph()
        user_run = Run("User: {}\n".format(user_question))
        user_run.Foreground = Brushes.Red
        user_paragraph.Inlines.Add(user_run)
        self.ConversationHistory.Document.Blocks.Add(user_paragraph)

        # Get response from ChatGPT
        response_text = ask_chatgpt(user_question)

        # Add ChatGPT's response in green to the ConversationHistory RichTextBox
        bot_paragraph = Paragraph()
        bot_run = Run("AskRev: {}\n\n".format(response_text))
        bot_run.Foreground = Brushes.Green
        bot_paragraph.Inlines.Add(bot_run)
        self.ConversationHistory.Document.Blocks.Add(bot_paragraph)

        # Clear the QuestionInput TextBox
        self.QuestionInput.Text = ""

        # Scroll to the bottom of the ConversationHistory RichTextBox
        self.ConversationHistory.ScrollToEnd()

# Show the dialog window
try:
    ChatGPTForm().ShowDialog()
except Exception as e:
    print("An error occurred while displaying the form:", e)
