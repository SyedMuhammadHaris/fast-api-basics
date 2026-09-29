from openai import OpenAI
import json
import os


# ============================================================
# 1. CREATE GROQ CLIENT
# ============================================================

# The OpenAI Python package can also be used with Groq because
# Groq provides an OpenAI-compatible API.
#
# base_url tells the OpenAI client:
# "Don't send requests to OpenAI. Send them to Groq."
#
# IMPORTANT:
# Never hard-code your API key in source code.
# Set it as an environment variable instead:
#
# Windows PowerShell:
# $env:GROQ_API_KEY="your-groq-api-key"
#
# Then Python can read it using os.environ.

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# 2. OUR ACTUAL PYTHON TOOLS
# ============================================================

# These are normal Python functions.
#
# The AI does NOT execute these functions.
#
# The AI only tells our Python program:
# "I want you to call get_weather with city='Karachi'."
#
# Our Python code then actually executes the function.


def get_weather(city: str):
    """
    Get weather information for a city.

    In a real application, this function could call:
    - Weather API
    - Database
    - Internal service
    """

    return f"The weather in {city} is sunny and 30°C."


def get_time(city: str):
    """
    Get the current time for a city.

    This is just dummy data for our example.
    In a real application, this could use a time API.
    """

    return f"The current time in {city} is 3:30 PM."


def calculate(a: float, b: float):
    """
    Add two numbers.

    This is the actual Python function that will perform
    the calculation when the AI requests this tool.
    """

    return a + b


# ============================================================
# 3. DESCRIBE OUR TOOLS TO THE AI
# ============================================================

# IMPORTANT:
#
# The AI cannot see our Python functions automatically.
#
# We have to tell the AI:
#
# - What tools exist
# - What each tool does
# - What parameters each tool expects
#
# These definitions are called "tool schemas".
#
# The schema does NOT contain the Python implementation.
# It only tells the model how the tool can be used.


tools = [

    # --------------------------------------------------------
    # TOOL 1: get_weather
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            # Name that the AI will use when requesting this tool.
            "name": "get_weather",

            # Description helps the AI decide when this tool
            # should be used.
            "description": "Get the weather for a city.",

            # Describe the arguments that the tool accepts.
            "parameters": {

                # The arguments must be a JSON object.
                "type": "object",

                # Available arguments.
                "properties": {

                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },

                # city is required.
                "required": ["city"],
            },
        },
    },


    # --------------------------------------------------------
    # TOOL 2: get_time
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "get_time",

            "description": "Get the current time for a city.",

            "parameters": {

                "type": "object",

                "properties": {

                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },

                "required": ["city"],
            },
        },
    },


    # --------------------------------------------------------
    # TOOL 3: calculate
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "calculate",

            "description": "Add two numbers together.",

            "parameters": {

                "type": "object",

                "properties": {

                    "a": {
                        "type": "number"
                    },

                    "b": {
                        "type": "number"
                    },
                },

                # Both numbers are required.
                "required": ["a", "b"],
            },
        },
    },
]


# ============================================================
# 4. CONNECT TOOL NAMES TO REAL PYTHON FUNCTIONS
# ============================================================

# This is VERY important.
#
# The AI knows the tool name:
#
#     "get_time"
#
# But Python needs to know:
#
#     Which actual Python function should I execute?
#
# This dictionary creates that connection.


tool_functions = {

    "get_weather": get_weather,

    "get_time": get_time,

    "calculate": calculate,
}


# ============================================================
# 5. USER'S QUESTION
# ============================================================

# This is what the user asks the AI.

user_message = "What time is it in Karachi?"

# You can test multiple tools with one question:
#
# user_message = (
#     "What is 25 + 75? Also, what is the weather in New York "
#     "and the current time in London?"
# )


# ============================================================
# 6. CREATE THE CONVERSATION
# ============================================================

# The Chat Completions API expects messages.
#
# Each message has a role:
#
# user      -> user question
# assistant -> AI response
# tool      -> result returned by our Python function
#
# Initially, we only have the user's message.

messages = [
    {
        "role": "user",
        "content": user_message
    }
]


# ============================================================
# 7. SEND USER QUESTION + TOOLS TO GROQ
# ============================================================

response = client.chat.completions.create(

    # Groq model.
    model="openai/gpt-oss-120b",

    # Conversation history.
    messages=messages,

    # Tell the AI what tools are available.
    tools=tools,
)


# ============================================================
# 8. LOOK AT THE MODEL'S FIRST RESPONSE
# ============================================================

print("Model response:")
print(response)

print("Model message:")
print(response.choices[0].message)


# ============================================================
# 9. GET THE AI'S MESSAGE
# ============================================================

# response contains a lot of information.
#
# response.choices[0].message is the actual message
# generated by the AI.

assistant_message = response.choices[0].message


# ============================================================
# 10. CHECK WHETHER AI REQUESTED A TOOL
# ============================================================

# tool_calls will contain the functions that the AI wants
# our Python program to execute.
#
# Example:
#
# User:
#     What time is it in Karachi?
#
# AI might return:
#
#     tool_calls = [
#         {
#             function:
#                 name = "get_time"
#                 arguments = '{"city": "Karachi"}'
#         }
#     ]
#
# If the AI doesn't need a tool, tool_calls will be None.


if assistant_message.tool_calls:

    # ========================================================
    # 11. SAVE AI'S TOOL-CALL MESSAGE
    # ========================================================

    # We add the AI message to our conversation history.
    #
    # This is important because the next model request needs
    # to know that the AI previously requested a tool.

    messages.append(assistant_message)


    # ========================================================
    # 12. PROCESS EVERY TOOL CALL
    # ========================================================

    # The model can request more than one tool.
    #
    # For example:
    #
    # "What is 25 + 75 and what time is it in Karachi?"
    #
    # could result in:
    #
    # calculate(...)
    # get_time(...)

    for tool_call in assistant_message.tool_calls:


        # ====================================================
        # 13. GET TOOL NAME
        # ====================================================

        # Example:
        #
        # tool_call.function.name
        #
        # gives:
        #
        # "get_time"

        tool_name = tool_call.function.name


        # ====================================================
        # 14. GET TOOL ARGUMENTS
        # ====================================================

        # The AI sends arguments as a JSON string.
        #
        # Example:
        #
        # '{"city": "Karachi"}'
        #
        # json.loads() converts that JSON string into
        # a normal Python dictionary:
        #
        # {
        #     "city": "Karachi"
        # }

        arguments = json.loads(
            tool_call.function.arguments
        )


        print("AI selected tool:", tool_name)
        print("Arguments:", arguments)


        # ====================================================
        # 15. FIND THE ACTUAL PYTHON FUNCTION
        # ====================================================

        # Suppose AI selected:
        #
        #     "get_time"
        #
        # Our dictionary contains:
        #
        #     "get_time": get_time
        #
        # So this gives us the actual Python function.

        function = tool_functions[tool_name]


        # ====================================================
        # 16. EXECUTE THE PYTHON FUNCTION
        # ====================================================

        # If arguments are:
        #
        # {
        #     "city": "Karachi"
        # }
        #
        # Then:
        #
        # function(**arguments)
        #
        # becomes:
        #
        # get_time(city="Karachi")

        result = function(**arguments)


        print("Tool result:", result)


        # ====================================================
        # 17. SEND TOOL RESULT BACK INTO CONVERSATION
        # ====================================================

        # The AI does NOT automatically know what our Python
        # function returned.
        #
        # We therefore add a "tool" message.
        #
        # Example:
        #
        # {
        #     "role": "tool",
        #     "tool_call_id": "call_123",
        #     "content": "The current time in Karachi is 3:30 PM."
        # }

        messages.append(
            {
                "role": "tool",

                # This ID connects the result to the exact
                # tool call made by the AI.
                "tool_call_id": tool_call.id,

                # Actual result returned by our Python function.
                "content": str(result),
            }
        )


    # ========================================================
    # 18. ASK THE AI FOR THE FINAL HUMAN-FRIENDLY ANSWER
    # ========================================================

    # At this point our conversation contains:
    #
    # USER:
    #     What time is it in Karachi?
    #
    # ASSISTANT:
    #     I want to call get_time(city="Karachi")
    #
    # TOOL:
    #     The current time in Karachi is 3:30 PM.
    #
    # Now we ask the AI to use that tool result and
    # produce the final answer.

    final_response = client.chat.completions.create(
  
        model="openai/gpt-oss-120b",

        messages=messages,
    )


    # ========================================================
    # 19. PRINT FINAL ANSWER
    # ========================================================

    print("Final answer:")

    print(
        final_response.choices[0].message.content
    )


# ============================================================
# 20. IF AI DID NOT REQUEST A TOOL
# ============================================================

else:

    # Sometimes the AI can answer directly without using
    # any tool.
    #
    # In that situation:
    #
    # assistant_message.tool_calls == None
    #
    # So we simply print the AI's answer.

    print("Final answer:")

    print(assistant_message.content)