import streamlit as st
import json
from google import genai
from config import config

# Set up Gemini API
client = genai.Client(api_key=config.GEMINI_API_KEY)

# Passwords for different users
USER_PASSWORDS = {
    "user": "zach",
    "girlfriend": "mal",
    "guest": "guest"
}

# Function to save workout data to a JSON file
def save_workout(user, workout_data):
    # Ensure the workout data includes all expected keys
    workout_data.setdefault("type", "Unknown Type")
    workout_data.setdefault("goal", "Unknown Goal")
    workout_data.setdefault("duration", 30)  # Default duration in minutes
    workout_data.setdefault("plan", "No workout plan generated.")
    
    try:
        with open(f"{user}_workouts.json", "a") as f:
            json.dump(workout_data, f)
            f.write("\n")  # Add a newline for each new workout
    except Exception as e:
        st.error(f"Error saving workout: {str(e)}")

# Function to load workout data
def load_workouts(user):
    try:
        with open(f"{user}_workouts.json", "r") as f:
            workouts = [json.loads(line) for line in f.readlines()]
        
        # Ensure each workout contains all required keys
        for workout in workouts:
            workout.setdefault("type", "Unknown Type")
            workout.setdefault("goal", "Unknown Goal")
            workout.setdefault("duration", 30)  # Default duration
            workout.setdefault("plan", "No workout plan generated.")
        
        return workouts
    except FileNotFoundError:
        return []

# Function to generate a workout using Gemini
def generate_workout(workout_type, fitness_level, duration, goal):
    prompt = f"Create a {fitness_level} level {workout_type} workout plan for {duration} minutes focused on {goal}. Include warm-up and cool-down exercises."
    
    try:
        # Generate text using Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # You can change the model version as needed
            contents=prompt
        )
        return response.text  # Extract the response text
    except Exception as e:
        st.error(f"Error generating workout: {str(e)}")
        return None

# Main app function
def main():
    st.title("Fitness Trainer App")

    # Login system
    password = st.text_input("Enter your password", type="password")
    
    if password == USER_PASSWORDS["user"]:
        st.session_state.user = "user"
        st.success("Welcome back, User!")
    elif password == USER_PASSWORDS["girlfriend"]:
        st.session_state.user = "girlfriend"
        st.success("Welcome back, Girlfriend!")
    elif password == USER_PASSWORDS["guest"]:
        st.session_state.user = "guest"
        st.success("Welcome, Guest!")
    else:
        st.warning("Invalid password. Please try again.")
        return

    # Load past workouts for the user
    workouts = load_workouts(st.session_state.user)

    # Display workout history in a gallery format in the sidebar
    if workouts:
        st.sidebar.title("Your Past Workouts")
        workout_options = {}
        for idx, workout in enumerate(workouts[::-1]):  # Reversed to show most recent first
            workout_label = f"{workout['type']} - {workout['goal']} - {workout['duration']} minutes"
            workout_options[workout_label] = workout
        selected_workout_label = st.sidebar.radio("Select a past workout:", list(workout_options.keys()))

        # Show selected workout details
        selected_workout = workout_options[selected_workout_label]
        st.sidebar.write(f"**Workout Details**")
        st.sidebar.write(f"Type: {selected_workout['type']}")
        st.sidebar.write(f"Duration: {selected_workout['duration']} minutes")
        st.sidebar.write(f"Goal: {selected_workout['goal']}")
        st.sidebar.write(f"Plan:\n{selected_workout['plan']}")

    # Display form for generating a new workout
    st.write("Generate a new workout!")
    workout_type = st.selectbox("Choose workout type", ["Running", "Weightlifting", "Cardio", "Swimming"])
    fitness_level = st.selectbox("Select your fitness level", ["Beginner", "Intermediate", "Advanced"])
    duration = st.number_input("Workout duration (minutes)", min_value=10, max_value=120, value=30)
    goal = st.selectbox("Select your fitness goal", ["Improve Endurance", "Build Muscle", "Increase Speed", "Lose Weight"])

    if st.button("Generate Workout"):
        new_workout = generate_workout(workout_type, fitness_level, duration, goal)
        if new_workout:
            st.write(new_workout)
            save_workout(st.session_state.user, {"type": workout_type, "duration": duration, "goal": goal, "plan": new_workout})
            st.success("New workout generated and saved!")

# Run the app
if __name__ == "__main__":
    main()
