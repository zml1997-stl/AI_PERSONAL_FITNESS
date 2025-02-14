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
    workout_data.setdefault("type", "Unknown Type")
    workout_data.setdefault("goal", "Unknown Goal")
    workout_data.setdefault("duration", 30)
    workout_data.setdefault("plan", "No workout plan generated.")
    
    try:
        with open(f"{user}_workouts.json", "a") as f:
            json.dump(workout_data, f)
            f.write("\n")
    except Exception as e:
        st.error(f"Error saving workout: {str(e)}")

# Function to load workout data
def load_workouts(user):
    try:
        with open(f"{user}_workouts.json", "r") as f:
            workouts = [json.loads(line) for line in f.readlines()]
        
        for workout in workouts:
            workout.setdefault("type", "Unknown Type")
            workout.setdefault("goal", "Unknown Goal")
            workout.setdefault("duration", 30)
            workout.setdefault("plan", "No workout plan generated.")
        
        return workouts
    except FileNotFoundError:
        return []

# Function to generate a workout using Gemini
def generate_workout(problem, fitness_goal, time_available, focus_area, output_style):
    prompt = f"""
    You are an expert fitness coach. I am {problem}. Recommend a workout for today tailored for someone aiming to {fitness_goal}. 
    I have {time_available} minutes, focusing primarily on {focus_area}. 
    I want you to {output_style}. 
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
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
        for idx, workout in enumerate(workouts[::-1]):
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

    # Form for generating a new workout
    st.write("Generate a new workout!")
    problem = st.text_input("Describe your problem or need (e.g., 'I feel fatigued and need recovery')", "")
    fitness_goal = st.selectbox("Select your fitness goal", ["Build Muscle", "Improve Endurance", "Increase Speed", "Lose Weight", "Flexibility"])
    time_available = st.number_input("Available time (minutes)", min_value=10, max_value=120, value=30)
    focus_area = st.text_input("Which area would you like to focus on (e.g., 'legs, arms, cardio, flexibility')", "")
    output_style = st.selectbox("How would you like the workout output?", 
                                ["Include warm-up, main workout, and cool-down",
                                 "Provide sets, reps, and rest time",
                                 "Simple plan without too many details"])

    if st.button("Generate Workout"):
        if problem and fitness_goal and time_available and focus_area:
            new_workout = generate_workout(problem, fitness_goal, time_available, focus_area, output_style)
            if new_workout:
                st.write(new_workout)
                save_workout(st.session_state.user, {"type": "Custom", "duration": time_available, "goal": fitness_goal, "plan": new_workout})
                st.success("New workout generated and saved!")
        else:
            st.warning("Please fill out all fields before generating a workout.")

# Run the app
if __name__ == "__main__":
    main()
