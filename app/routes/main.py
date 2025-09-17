from flask import Blueprint,  Flask, render_template, request, redirect, url_for ,jsonify

main = Blueprint("main", __name__)

subject_responses = {
    "math": "For math assignments, focus on breaking down the problem into smaller steps. Remember to check your work using a different method.",
    "english": "In English, a strong thesis statement is key. Structure your essays with clear topic sentences and provide evidence from the text to support your claims.",
    "kiswahili": "Katika Kiswahili, zingatia sarufi na matumizi sahihi ya maneno. Jenga sentensi fupi na zenye maana ili kujibu maswali ya insha.",
    "physics": "Physics problems require understanding the core principles and formulas. Draw a free-body diagram to visualize the forces at play.",
    "biology": "When studying Biology, use diagrams to help you remember complex processes. Practice labeling and explaining the functions of different parts of a cell or organ.",
    "chemistry": "In Chemistry, balancing equations and understanding chemical reactions is crucial. Pay attention to the periodic table and the properties of elements.",
    "cre": "CRE assignments often require you to reflect on moral and spiritual themes. Reference specific Bible stories and teachings to support your arguments.",
    "business studies": "For Business Studies, identify key terms and apply them to real-world scenarios. Focus on the relationship between supply, demand, and market trends.",
    "geography": "Geography involves understanding the Earth's physical and human systems. Use maps and data analysis to support your answers on topics like climate or population.",
    "history": "To tackle History assignments, remember to analyze both the causes and effects of events. A timeline can help you organize key dates and figures.",
    "agriculture": "In Agriculture, practical knowledge is as important as theory. Learn about different farming methods and crop cycles.",
    "music": "Music theory questions require a solid understanding of scales, chords, and harmony. Listen to different pieces to train your ear.",
    "french": "Pour le français, concentrez-vous sur la grammaire et la conjugaison. Pratiquez votre prononciation et votre vocabulaire chaque jour.",
    "german": "Für Deutschaufgaben, üben Sie die Grammatik und die Satzstruktur. Lernen Sie neue Wörter, um Ihren Wortschatz zu erweitern.",
    "homescience": "Home Science assignments cover a variety of topics. Focus on understanding nutrition, healthy living, and effective resource management."
}

@main.route("/")
def home():
    return render_template("homepage.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/testimonials")
def testimonials():
    return render_template("testimonials.html")

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        preferred_method = request.form.get('preferred_method')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Here you would process the data. For example:
        # 1. Save it to a database.
        # 2. Send an email to the school's support team with the message.
        # 3. Use an external service to handle the form submission.

        print("Form submitted with the following data:")
        print(f"Name: {first_name} {last_name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        
        # After processing, you should redirect the user to a new page
        # or back to the contact page with a success message.
        return redirect(url_for('main.contact')) # Redirect back to the contact page for now

    # If the request is a GET, simply render the template with the form
    return render_template('contact.html')

@main.route("/edubot_chat", methods=["POST"])
def edubot_chat():
    """Handles chatbot conversations and returns responses."""
    user_message = request.json.get("message", "").lower()
    response_message = "I'm sorry, I don't understand that. I can provide general advice on a specific subject, like 'math' or 'history'. Just ask!"

    # Check for keywords to provide a subject-specific response
    for subject, response in subject_responses.items():
        if subject in user_message:
            response_message = response
            break # Exit the loop once a subject is found

    # Handle general greetings and queries
    if "hello" in user_message or "hi" in user_message:
        response_message = "Hello! I'm EduBot. I can provide tips for your assignments in various subjects. Just ask me about a subject like 'physics' or 'biology'."
    elif "contact" in user_message or "help" in user_message:
        response_message = "You can contact our support team at support@edusystem.com."
    
    return jsonify({"message": response_message})