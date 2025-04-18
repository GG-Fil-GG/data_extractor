import logging
from typing import Dict, List, Optional
from functools import wraps
import tiktoken
from datetime import datetime
import uuid

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class QueryManager:
    def __init__(self, job_manager):
        self.job_manager = job_manager
        self.context_window = 128000  # GPT-4o context window
        self.max_history_messages = 10  # Maximum number of messages to keep in history
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Tokenizer for GPT-4o

    @handle_errors
    def create_thread(self, title: str) -> Dict:
        """
        Create a new thread in the job data.
        
        Args:
            title: Display title for the thread
            
        Returns:
            Dict: Created thread
        """
        thread = {
            "id": str(uuid.uuid4()),
            "title": title,
            "status": "initialized",
            "messages": [],
            "queries": []
        }
        self.job_manager.job_data["threads"].append(thread)
        self.job_manager.job_data["state"]["threads"]["total_threads"] += 1
        logging.info(f"Created new thread: {thread['id']}")
        return thread

    @handle_errors
    def add_message(self, thread_id: str, role: str, content: str) -> Dict:
        """
        Add a message to a thread's history.
        
        Args:
            thread_id: Thread identifier
            role: Message role (user/assistant)
            content: Message content
            
        Returns:
            Dict: Added message
        """
        thread = self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
            
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        thread["messages"].append(message)
        
        # Ensure we don't exceed context window
        self._manage_context_window(thread_id)
        
        logging.info(f"Added {role} message to thread {thread_id}")
        return message

    def _manage_context_window(self, thread_id: str):
        """
        Ensure thread history fits within context window.
        Removes oldest messages if necessary.
        
        Args:
            thread_id: Thread identifier
        """
        thread = self.get_thread(thread_id)
        if not thread:
            return
            
        while len(thread["messages"]) > self.max_history_messages:
            thread["messages"].pop(0)
            logging.info(f"Removed message from thread {thread_id} to manage context window")

    @handle_errors
    def get_thread_history(self, thread_id: str) -> List[Dict]:
        """
        Retrieve thread history for context.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            List[Dict]: List of messages in the thread
        """
        thread = self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
            
        return thread["messages"]

    @handle_errors
    def update_thread_status(self, thread_id: str, status: str):
        """
        Update the status of a thread.
        
        Args:
            thread_id: Thread identifier
            status: New status
        """
        thread = self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
            
        thread["status"] = status
        
        # Update overall thread state
        state = self.job_manager.job_data["state"]["threads"]
        if status == "complete":
            state["completed_threads"] += 1
        elif status == "failed":
            state["failed_threads"].append(thread_id)
            
        if state["completed_threads"] == state["total_threads"]:
            state["status"] = "complete"
        elif state["failed_threads"]:
            state["status"] = "failed"
        else:
            state["status"] = "in_progress"
            
        logging.info(f"Updated thread {thread_id} status to {status}")

    @handle_errors
    def get_thread(self, thread_id: str) -> Optional[Dict]:
        """
        Retrieve thread information.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Optional[Dict]: Thread information if found
        """
        return next(
            (thread for thread in self.job_manager.job_data["threads"] if thread["id"] == thread_id),
            None
        )

    @handle_errors
    def cleanup_thread(self, thread_id: str):
        """
        Clean up a thread's resources.
        
        Args:
            thread_id: Thread identifier
        """
        thread = self.get_thread(thread_id)
        if thread:
            self.job_manager.job_data["threads"].remove(thread)
            logging.info(f"Cleaned up thread {thread_id}")

    @handle_errors
    def process_query(self, thread_id: str, query_id: str) -> Dict:
        """
        Process a query within an existing thread.
        
        Args:
            thread_id: Thread identifier
            query_id: Query identifier to process
            
        Returns:
            Dict: Processing result including response and metadata
        """
        thread = self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
            
        # Find the query in thread
        query = next(
            (q for q in thread["queries"] if q["id"] == query_id),
            None
        )
        if not query:
            raise ValueError(f"Query {query_id} not found in thread {thread_id}")
            
        # Add user query
        self.add_message(thread_id, "user", query["text"])
        
        # Update thread status
        self.update_thread_status(thread_id, "processing")
        
        try:
            # Get thread history for context
            messages = self.get_thread_history(thread_id)
            
            # Call LLMInterface to process the query
            response = self.llm_interface.process_messages(messages)
            
            # Add assistant response to thread
            self.add_message(thread_id, "assistant", response)
            
            # Update thread status
            self.update_thread_status(thread_id, "complete")
            
            return {
                "thread_id": thread_id,
                "query_id": query_id,
                "response": response,
                "format": query["format"]
            }
            
        except Exception as e:
            self.update_thread_status(thread_id, "failed")
            raise
