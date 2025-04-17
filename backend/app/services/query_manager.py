import logging
from typing import Dict, List, Optional
from functools import wraps
import tiktoken
from datetime import datetime

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
        self.threads: Dict[str, Dict] = {}  # Store thread states
        self.context_window = 128000  # GPT-4o context window
        self.max_history_messages = 10  # Maximum number of messages to keep in history
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Tokenizer for GPT-4o
        
        # Initialize query state in job data
        if "queries" not in self.job_manager.job_data["state"]:
            self.job_manager.job_data["state"]["queries"] = {
                "total_queries": 0,
                "processed_queries": 0,
                "failed_queries": [],
                "status": "pending"
            }

    @handle_errors
    def create_thread(self, thread_id: str) -> Dict:
        """
        Initialize a new conversation thread.
        Adds the system_message from job data as the initial developer message.
        
        Args:
            thread_id: Unique identifier for the thread
            
        Returns:
            Dict: Thread state information
        """
        thread = {
            "id": thread_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
            "token_count": 0,
            "status": "pending",
            "last_response_id": None,
            "error": None
        }
        
        self.threads[thread_id] = thread
        
        # Add system_message as initial developer message
        system_message = self.job_manager.job_data.get("system_message")
        if system_message:
            self.add_message(thread_id, "developer", system_message)
        
        logging.info(f"Created new thread {thread_id}")
        return thread

    @handle_errors
    def add_message(self, thread_id: str, role: str, content: str) -> Dict:
        """
        Add a message to a thread's history.
        
        Args:
            thread_id: Thread identifier
            role: Message role (user/assistant/developer)
            content: Message content
            
        Returns:
            Dict: Added message
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist")
            
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "token_count": len(self.encoding.encode(content))
        }
        
        thread = self.threads[thread_id]
        thread["messages"].append(message)
        thread["token_count"] += message["token_count"]
        
        # Ensure we don't exceed context window
        self._manage_context_window(thread_id)
        
        logging.info(f"Added {role} message to thread {thread_id}")
        return message

    def _manage_context_window(self, thread_id: str):
        """
        Ensure thread history fits within context window.
        Removes oldest messages if necessary, but preserves the system message.
        
        Args:
            thread_id: Thread identifier
        """
        thread = self.threads[thread_id]
        
        # Keep the system message (first developer message) if it exists
        system_message = None
        if thread["messages"] and thread["messages"][0]["role"] == "developer":
            system_message = thread["messages"].pop(0)
            thread["token_count"] -= system_message["token_count"]
        
        # Remove oldest messages if we exceed the context window
        while (thread["token_count"] > self.context_window or 
               len(thread["messages"]) > self.max_history_messages):
            if not thread["messages"]:
                break
                
            removed_message = thread["messages"].pop(0)
            thread["token_count"] -= removed_message["token_count"]
            
            logging.info(f"Removed message from thread {thread_id} to manage context window")
        
        # Restore system message if it was removed
        if system_message:
            thread["messages"].insert(0, system_message)
            thread["token_count"] += system_message["token_count"]

    @handle_errors
    def get_thread_history(self, thread_id: str) -> List[Dict]:
        """
        Retrieve thread history for context.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            List[Dict]: List of messages in the thread
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist")
            
        return self.threads[thread_id]["messages"]

    @handle_errors
    def update_thread_status(self, thread_id: str, status: str, error: Optional[str] = None):
        """
        Update the status of a thread.
        
        Args:
            thread_id: Thread identifier
            status: New status (pending/processing/complete/failed)
            error: Error message if status is failed
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist")
            
        thread = self.threads[thread_id]
        thread["status"] = status
        
        if error:
            thread["error"] = error
            self.job_manager.job_data["state"]["queries"]["failed_queries"].append(thread_id)
        elif status == "complete":
            self.job_manager.job_data["state"]["queries"]["processed_queries"] += 1
            
        # Update overall query status
        self._update_overall_query_status()
        
        logging.info(f"Updated thread {thread_id} status to {status}")

    def _update_overall_query_status(self):
        """Update the overall query processing status."""
        state = self.job_manager.job_data["state"]["queries"]
        total = state["total_queries"]
        processed = state["processed_queries"]
        failed = len(state["failed_queries"])
        
        if failed > 0:
            state["status"] = "failed"
        elif processed == total:
            state["status"] = "complete"
        elif processed > 0:
            state["status"] = "in_progress"
        else:
            state["status"] = "pending"

    @handle_errors
    def get_thread(self, thread_id: str) -> Dict:
        """
        Retrieve thread information.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Dict: Thread state information
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist")
            
        return self.threads[thread_id]

    @handle_errors
    def cleanup_thread(self, thread_id: str):
        """
        Clean up a thread's resources.
        
        Args:
            thread_id: Thread identifier
        """
        if thread_id in self.threads:
            del self.threads[thread_id]
            logging.info(f"Cleaned up thread {thread_id}")

    def get_query_state(self) -> Dict:
        """
        Get the current state of all queries.
        
        Returns:
            Dict: Query processing state
        """
        return self.job_manager.job_data["state"]["queries"]

    @handle_errors
    def process_query(self, thread_id: str, query_text: str) -> Dict:
        """
        Process a query within an existing thread.
        The thread should already have the system_message as its initial developer message.
        
        Args:
            thread_id: Thread identifier
            query_text: The query text to process
            
        Returns:
            Dict: Processing result including response and metadata
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist")
            
        # Add user query
        self.add_message(thread_id, "user", query_text)
        
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
                "response": response,
                "status": "complete"
            }
            
        except Exception as e:
            self.update_thread_status(thread_id, "failed", str(e))
            raise
