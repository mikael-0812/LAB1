import logging

# Configure logging to write to results.log
logging.basicConfig(filename='results.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_event(event_type, system, question=None, item=None, details=None):
    """
    Log an event with detailed information.
    Parameters:
    - event_type: e.g., 'response', 'thought', 'action', 'observation'
    - system: 'Chatbot' or 'Agent'
    - question: The question asked (optional)
    - item: The specific item or topic (optional)
    - details: Additional details like answer, thought content, etc.
    """
    message = f"Event: {event_type}, System: {system}"
    if question:
        message += f", Question: {question}"
    if item:
        message += f", Item: {item}"
    if details:
        message += f", Details: {details}"
    logging.info(message)

def log_result(system, question, item, answer):
    """
    Log the final result of a system response.
    This is a wrapper for backward compatibility.
    """
    log_event('response', system, question, item, answer)