from chatbot_baseline import ChatbotBaseline
from agent import ReActAgent
import logger

def run_tests():
    """
    Run 5 test cases for both ChatbotBaseline and ReActAgent.
    Print results and log them.
    """
    chatbot = ChatbotBaseline()
    agent = ReActAgent()

    test_cases = [
        {
            'question': 'What is the price of T-Shirt Basic in fashion store?',
            'item': 'T-Shirt Basic'
        },
        {
            'question': 'What are the prerequisites for Course 1?',
            'item': 'Course 1'
        },
        {
            'question': 'Is Restaurant 1 open?',
            'item': 'Restaurant 1'
        },
        {
            'question': 'What is the flight price to Destination?',
            'item': 'Destination'
        },
        {
            'question': 'What is the balance of ACC001?',
            'item': 'ACC001'
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test['question']}")

        # Chatbot response
        chatbot_answer = chatbot.respond(test['question'])
        print(f"Chatbot Answer: {chatbot_answer}")
        logger.log_event('response', 'Chatbot', test['question'], test['item'], chatbot_answer)

        # Agent response
        agent_answer = agent.run(test['question'])
        print(f"Agent Answer: {agent_answer}")
        # Agent already logs its response in run method

if __name__ == "__main__":
    run_tests()