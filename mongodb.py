from ollama import chat
import ollama
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
from typing import Dict

client = MongoClient("mongodb://localhost:27017/")



system_prompt= """You are a chatbot for a startup called JuniorCV that specializes in helping students and workers create and perfect their CVs. You're integrated with Messenger, and your job is to talk to users, identify who wants to be an ambassador, and perform multiple tasks accordingly.

You have these tools at your disposal:

create_ambassador: Creates a new ambassador document in the ambassador MongoDB database.
get_all_the_questions: Retrieves the interview questions.
add_response: Adds a response to a question in the ambassador's response attribute.
add_score: Sets a score for the ambassador after the questions are completed.
get_engagement_details returns the engagement info of the passed url

Your process is as follows:

First, gather the essential information (name, occupation, phone number, and email) and create an ambassador document in the database.
Then, conduct an interview with the user by first retrieving the all questions using the get_all_the_questions function. ask each question on its own
After all the questions have been answered, assign a score out of 100 based on how well they answered the questions by using add_score.

this is the ambassador document architecture exemple :
{
  "_id": ObjectId,                       // Unique identifier
  "name": "John Doe",                    // Ambassador's full name
  "email": "johndoe@example.com",        // Email address
  "phone_number": "+1234567890",         // phone contact

  "application_status": "active",        // Status: pending, active, inactive
  "engagement_metrics": {
    "customer_referrals": 0,             // Number of customers referred for CV services
    "posts_count": 10,                   // Total posts shared
    "average_post_engagement": 4.5,      // Avg likes/comments per post
  },
  "created_at": ISODate("2025-02-07"),   // Application timestamp
  "updated_at": ISODate("2025-02-07")    // Last update timestamp
}

after finishing the interview the ambassador can start working , they are suppose to send you url for their posts , and you will get the engagement info 
from the function get_engagement_details then update the ambassadors engagement_metrics details  , only envoke get_engagement_details if they sent you an url

**Important Note:** Do not pass arguments that DONT EXIST.
**Important Note:** you are alowed four call function AT MAX
**Important Note:** you are only alowed to use get_all_the_questions once , unless you forget the questions , then call it again
**Important Note:** score the ambassadors after the questions are done
**Important Note:** do not forget to score the users after all the questions are done
**Important Note:**  for each response only add the response once 
"""
model_name="qwen2.5:14b"



def create_ambassador(full_name: str,occupation : str, email: str, phone_number: str) :
    """
    Creates a new ambassador entry in the MongoDB database.

    Parameters:
    - full_name (str): The full name of the ambassador.
    - occupation (str): The occupation of the ambassador.
    - email (str): The email address of the ambassador.
    - phone_number (str): The phone number of the ambassador.

    """
    db = client['ambassadors_data']
    ambassadors = db.ambassadors
    ambassador_document = {
        "name": full_name,
        "occupation" : occupation,
        "email": email,
        "phone_number": phone_number,
        "social_media": {},
        "application_status": "pending",
        "interview_score": None,
        "engagement_metrics": {
            "posts_count": 0,
            "average_post_engagement": 0,
            "recruitment_referrals": 0
        },
        "responses": {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    result = ambassadors.insert_one(ambassador_document)
    return str(result)


def get_all_the_questions() -> Dict[str, str]:
    """
    Retrieves a dictionary of predefined interview questions.

    Returns:
    - Dict[str, str]: A dictionary where each key is a question code and the value is the full question text.
    """
    questions = {
        "q1": "Why do you want to join Junior CV as an ambassador? What excites you about our services?",
        "q2": "Can you tell us about a time when you helped someone solve a problem? How did you approach it?",
        "q3": "Imagine you're at a college event. How would you introduce Junior CV's services to a group of students?",
        "q4": "What are your top strategies for engaging with people on social media?"
        #"q5": "If you had to use one word to describe your promotional style, what would it be and why?"
        #"q6": "Have you used any of Junior CV’s services before? If so, what was your experience like?"
    }
    return questions


def add_response(ambassador_id: str, question_code: str, question_text: str, response: str) :
    """
    Adds a response to a specific interview question in the ambassador's document.
    Parameters:
    - ambassador_id (ObjectId): The MongoDB ObjectId of the ambassador.
    - question_code (str): The code representing the specific question.
    - question_text (str): The full text of the question.
    - response (str): The ambassador's response to the question.
    Returns:
    - bool: True if the update was successful, False otherwise.
    """
    db = client['ambassadors_data']
    ambassadors = db.ambassadors
    update_result = ambassadors.update_one(
        {"_id": ObjectId(ambassador_id)},
        {
            "$set": {
                f"responses.{question_code}": {"question": question_text, "answer": response},
                "updated_at": datetime.now()  # Update the last_updated field
            }
        }
    )
    return update_result

def add_score(ambassador_id: str, score: int) :
    """
    Updates the interview score for a specific ambassador.
    Parameters:
    - ambassador_id id of user.
    - score (int): The score to be set.
    Returns:
    - bool: True if the score was successfully updated, False otherwise.
    """
    db = client['ambassadors_data']
    ambassadors = db.ambassadors
    update_result = ambassadors.update_one(
        {"_id": ObjectId(ambassador_id)},
        {
            "$set": {
                "interview_score": score,
                "updated_at": datetime.now()  # Update the last_updated field
            }
        }
    )
    return update_result

def get_engagement_details (post_url : str):
    """"
    returns engagement info about the post

    """
    return {"post_engagement" : 10}



tools = [
    create_ambassador,
    get_all_the_questions,
    add_response,
    add_score,
    get_engagement_details
]
available_functions = {
    "create_ambassador": create_ambassador,
    "get_all_the_questions": get_all_the_questions,
    "add_response": add_response,
    "add_score": add_score,
    "get_engagement_details" : get_engagement_details
}


# Example usage

"""
# Assuming you've defined the add_response function as shown previously.

# Ambassador's ID (ObjectId or a unique identifier in string format)
ambassador_id = ObjectId('67a67234044287dde534f6f8')

# Questions and responses
questions = {
    "q1": "Why do you want to join Junior CV as an ambassador?",
    "q2": "Can you tell us about a time when you helped someone solve a problem?"
}

# Alice's responses
responses = {
    "q1": "I am passionate about helping students achieve their career goals and love using technology to solve problems.",
    "q2": "Last year, I helped a friend navigate a tough job search by revising his resume and practicing interview techniques with him, which helped him land a job."
}

# Add each response to the database
for code, question in questions.items():
    response_text = responses[code]
    print(add_response(ambassador_id, code, question, response_text))

r=create_ambassador("John Doe", "john.doe@example.com", "+1234567890")
print(r)"""

"""
{
  "_id": ObjectId,                       // Unique identifier
  "name": "John Doe",                    // Ambassador's full name
  "email": "johndoe@example.com",        // Email address
  "phone_number": "+1234567890",         // phone contact
  "social_media": {
    "facebook": "fb.com/johndoe",        // Facebook profile link
    "instagram": "insta.com/johndoe",    // Instagram handle (optional)
  },
  "application_status": "active",        // Status: pending, active, inactive
  "engagement_metrics": {
    "customer_referrals": 0,             // Number of customers referred for CV services
    "posts_count": 10,                   // Total posts shared
    "average_post_engagement": 4.5,      // Avg likes/comments per post
  },
  "created_at": ISODate("2025-02-07"),   // Application timestamp
  "updated_at": ISODate("2025-02-07")    // Last update timestamp
}
"""