"""
communication_protocol.py

This file defines the communication protocol used by all agents in the Smart Home Energy Management System.
It includes message types, message structures, and functions for sending and receiving messages between agents.

Usage:
- Enables seamless communication between agents (e.g., Behavioral Segmentation Agent, Prediction Agent, Demand Response Agent, etc.)
- Defines message formats for requests, responses, and notifications.

Inputs:
- Messages from other agents containing data like energy demand, predictions, appliance priority, etc.
- Responses or notifications based on actions taken by the agent.

Outputs:
- Structured messages for other agents in response to requests or updates.

Agents:
1. BehavioralSegmentationAgent
2. PredictionAgent
3. DemandResponseAgent
4. FacilitatingAgent
"""

class Message:
    """
    Represents a message exchanged between agents.
    
    Attributes:
    - sender: The name or ID of the agent sending the message.
    - receiver: The name or ID of the agent receiving the message.
    - message_type: Type of message (e.g., 'request', 'response', 'notification').
    - content: The content of the message (can be any type of data, usually a dictionary).
    - timestamp: Time when the message was sent.
    """
    def __init__(self, sender, receiver, message_type, content):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.timestamp = pd.Timestamp.now()

    def __repr__(self):
        return f"Message from {self.sender} to {self.receiver} - Type: {self.message_type} - Content: {self.content}"

class CommunicationProtocol:
    """
    Handles the sending and receiving of messages between agents.
    
    Provides methods for agents to send requests, responses, and notifications to each other.
    """

    def __init__(self):
        self.message_queue = []

    def send_message(self, sender, receiver, message_type, content):
        """
        Create a message and add it to the message queue.
        
        Args:
        sender (str): Name of the sending agent.
        receiver (str): Name of the receiving agent.
        message_type (str): Type of message ('request', 'response', 'notification').
        content (dict): Content of the message.
        """
        message = Message(sender, receiver, message_type, content)
        self.message_queue.append(message)
        print(f"Message sent: {message}")

    def receive_message(self, agent_name):
        """
        Receive all messages for the specified agent and process them.
        
        Args:
        agent_name (str): The name of the agent receiving the message.
        
        Returns:
        list: List of messages received by the agent.
        """
        received_messages = [msg for msg in self.message_queue if msg.receiver == agent_name]
        
        # Remove the received messages from the queue after they are processed.
        self.message_queue = [msg for msg in self.message_queue if msg.receiver != agent_name]
        
        return received_messages

    def process_message(self, agent_name):
        """
        Process all incoming messages for a specific agent. This method can be customized to handle different types
        of messages (e.g., by calling different agent methods).
        
        Args:
        agent_name (str): The name of the agent that will process the messages.
        
        Returns:
        None
        """
        messages = self.receive_message(agent_name)
        
        for message in messages:
            if message.message_type == "request":
                self.handle_request(message, agent_name)
            elif message.message_type == "response":
                self.handle_response(message, agent_name)
            elif message.message_type == "notification":
                self.handle_notification(message, agent_name)

    def handle_request(self, message, agent_name):
        """
        Handle a 'request' type message from another agent.
        
        Args:
        message (Message): The request message.
        agent_name (str): The name of the agent processing the message.
        
        Returns:
        None
        """
        print(f"Processing request from {message.sender} to {message.receiver}: {message.content}")
        # Implement custom request handling logic (e.g., respond with data or request further action)
        response_content = {"status": "acknowledged", "info": "Request processed successfully"}
        self.send_message(agent_name, message.sender, "response", response_content)

    def handle_response(self, message, agent_name):
        """
        Handle a 'response' type message from another agent.
        
        Args:
        message (Message): The response message.
        agent_name (str): The name of the agent processing the message.
        
        Returns:
        None
        """
        print(f"Received response from {message.sender}: {message.content}")
        # Implement custom response handling logic (e.g., adjust behavior based on received data)

    def handle_notification(self, message, agent_name):
        """
        Handle a 'notification' type message from another agent.
        
        Args:
        message (Message): The notification message.
        agent_name (str): The name of the agent processing the message.
        
        Returns:
        None
        """
        print(f"Received notification from {message.sender}: {message.content}")
        # Implement custom notification handling logic (e.g., adjust state or inform other agents)


# Example usage of the protocol
if __name__ == "__main__":
    # Create an instance of the communication protocol
    comm_protocol = CommunicationProtocol()

    # Simulate sending and receiving messages between agents
    comm_protocol.send_message(sender="PredictionAgent", receiver="BehavioralSegmentationAgent", message_type="request", content={"data": "energy forecast"})
    comm_protocol.process_message(agent_name="BehavioralSegmentationAgent")

    comm_protocol.send_message(sender="BehavioralSegmentationAgent", receiver="DemandResponseAgent", message_type="notification", content={"status": "appliance priorities updated"})
    comm_protocol.process_message(agent_name="DemandResponseAgent")
