import clr
import json
import os
import sys
import subprocess
from pyrevit import forms
from System.Windows.Documents import Run, Paragraph
from System.Windows.Media import Brushes
from Autodesk.Revit.UI import UIApplication
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInParameter

# Define paths to the external Python interpreter and main.py script
python_exe_path = r"" # Full path to Python executable
main_script_path = r"" # Full path to chatgpt_service.py

# Access the Revit document using UIApplication
uiapp = __revit__  # Get the Revit application from pyRevit's __revit__ variable
doc = uiapp.ActiveUIDocument.Document

# Path to the extracted data JSON file
data_path = os.path.join(os.path.expanduser("~"), "RevitModelData.json")


# Function to extract model data and save to JSON
def extract_model_data():
    elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
    all_data = []
    for el in elements:
        data = {
            "Id": el.Id.IntegerValue,
            "Category": el.Category.Name if el.Category else "N/A",
            "Name": el.Name if hasattr(el, "Name") else "Unnamed Element",
            "Volume": el.LookupParameter("Volume").AsDouble() if el.LookupParameter("Volume") else None,
            "Area": el.LookupParameter("Area").AsDouble() if el.LookupParameter("Area") else None,
            "Material": el.LookupParameter("Material").AsString() if el.LookupParameter("Material") else "Not Specified"
        }
        all_data.append(data)

    # Save extracted data to JSON
    with open(data_path, 'w') as f:
        json.dump(all_data, f, indent=4)

    return all_data


# Load data from file if available, otherwise extract it
if os.path.exists(data_path):
    with open(data_path, 'r') as f:
        model_data = json.load(f)
else:
    model_data = extract_model_data()


# Define query function to call OpenAI via subprocess
def query_data(question, model_data):
    input_data = json.dumps({
        "question": question,
        "model_data": model_data
    })

    # Run main.py with the question and model data as input
    try:
        process = subprocess.Popen(
            [python_exe_path, main_script_path],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate(input=input_data)

        if process.returncode != 0:
            return "Error: " + stderr.strip()

        return stdout.strip()
    except Exception as e:
        return "An error occurred: " + str(e)


# Main chat interface
class ModelChatForm(forms.WPFWindow):
    def __init__(self):
        xaml_path = os.path.join(os.path.dirname(__file__), "ModelChatForm.xaml")
        forms.WPFWindow.__init__(self, xaml_path)
        self.SendButton.Click += self.send_button_click

    def send_button_click(self, sender, args):
        user_question = self.QuestionInput.Text.strip()
        if user_question == "":
            return

        # Display user question in red
        user_paragraph = Paragraph()
        user_run = Run("User: {}\n".format(user_question))
        user_run.Foreground = Brushes.Red
        user_paragraph.Inlines.Add(user_run)
        self.ConversationHistory.Document.Blocks.Add(user_paragraph)

        # Get response from OpenAI's API via subprocess
        response_text = query_data(user_question, model_data)

        # Display response in green
        bot_paragraph = Paragraph()
        bot_run = Run("ModelMind: {}\n\n".format(response_text))
        bot_run.Foreground = Brushes.Green
        bot_paragraph.Inlines.Add(bot_run)
        self.ConversationHistory.Document.Blocks.Add(bot_paragraph)

        # Clear input and scroll to bottom
        self.QuestionInput.Text = ""
        self.ConversationHistory.ScrollToEnd()


try:
    ModelChatForm().ShowDialog()
except Exception as e:
    print("An error occurred:", e)
