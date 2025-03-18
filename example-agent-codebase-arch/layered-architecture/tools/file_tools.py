#!/usr/bin/env python3

"""
File service for the Layered Architecture implementation of the file editor agent.
"""

import os
import traceback
from typing import Dict, Any, Optional, List, Tuple, Union

import sys
import os

# Add the parent directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import FileOperationResult
from tools.logger import Logger, app_logger
from tools.path_utils import normalize_path, display_file_content

class FileService:
    """
    Service for handling file operations.
    """
    
    @staticmethod
    def view_file(path: str, view_range=None) -> FileOperationResult:
        """
        View the contents of a file.

        Args:
            path: The path to the file to view
            view_range: Optional start and end lines to view [start, end]

        Returns:
            FileOperationResult with content or error message
        """
        try:
            # Normalize the path
            path = normalize_path(path)

            if not os.path.exists(path):
                error_msg = f"File {path} does not exist"
                Logger.error(app_logger, f"[view_file] {error_msg}")
                return FileOperationResult(False, error_msg)

            with open(path, "r") as f:
                lines = f.readlines()

            if view_range:
                start, end = view_range
                # Convert to 0-indexed for Python
                start = max(0, start - 1)
                if end == -1:
                    end = len(lines)
                else:
                    end = min(len(lines), end)
                lines = lines[start:end]

            content = "".join(lines)

            # Display the file content (only for console, not returned to Claude)
            display_file_content(path, content)

            return FileOperationResult(True, f"Successfully viewed file {path}", content)
        except Exception as e:
            error_msg = f"Error viewing file: {str(e)}"
            Logger.error(app_logger, f"[view_file] {error_msg}", exc_info=True)
            return FileOperationResult(False, error_msg)

    @staticmethod
    def str_replace(path: str, old_str: str, new_str: str) -> FileOperationResult:
        """
        Replace a specific string in a file.

        Args:
            path: The path to the file to modify
            old_str: The text to replace
            new_str: The new text to insert

        Returns:
            FileOperationResult with result or error message
        """
        try:
            # Normalize the path
            path = normalize_path(path)

            if not os.path.exists(path):
                error_msg = f"File {path} does not exist"
                Logger.error(app_logger, f"[str_replace] {error_msg}")
                return FileOperationResult(False, error_msg)

            with open(path, "r") as f:
                content = f.read()

            if old_str not in content:
                error_msg = f"The specified string was not found in the file {path}"
                Logger.error(app_logger, f"[str_replace] {error_msg}")
                return FileOperationResult(False, error_msg)

            new_content = content.replace(old_str, new_str, 1)

            with open(path, "w") as f:
                f.write(new_content)

            Logger.info(app_logger, f"[str_replace] Successfully replaced text in {path}")
            return FileOperationResult(True, f"Successfully replaced text in {path}")
        except Exception as e:
            error_msg = f"Error replacing text: {str(e)}"
            Logger.error(app_logger, f"[str_replace] {error_msg}", exc_info=True)
            return FileOperationResult(False, error_msg)

    @staticmethod
    def create_file(path: str, file_text: str) -> FileOperationResult:
        """
        Create a new file with specified content.

        Args:
            path: The path where the new file should be created
            file_text: The content to write to the new file

        Returns:
            FileOperationResult with result or error message
        """
        try:
            # Check if the path is empty or invalid
            if not path or not path.strip():
                error_msg = "Invalid file path provided: path is empty."
                Logger.error(app_logger, f"[create_file] {error_msg}")
                return FileOperationResult(False, error_msg)

            # Normalize the path
            path = normalize_path(path)

            # Check if the directory exists
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                Logger.info(app_logger, f"[create_file] Creating directory: {directory}")
                os.makedirs(directory)

            with open(path, "w") as f:
                f.write(file_text or "")

            Logger.info(app_logger, f"[create_file] Successfully created file {path}")
            return FileOperationResult(True, f"Successfully created file {path}")
        except Exception as e:
            error_msg = f"Error creating file: {str(e)}"
            Logger.error(app_logger, f"[create_file] {error_msg}", exc_info=True)
            return FileOperationResult(False, error_msg)

    @staticmethod
    def insert_text(path: str, insert_line: int, new_str: str) -> FileOperationResult:
        """
        Insert text at a specific location in a file.

        Args:
            path: The path to the file to modify
            insert_line: The line number after which to insert the text
            new_str: The text to insert

        Returns:
            FileOperationResult with result or error message
        """
        try:
            if not path or not path.strip():
                error_msg = "Invalid file path provided: path is empty."
                Logger.error(app_logger, f"[insert_text] {error_msg}")
                return FileOperationResult(False, error_msg)

            # Normalize the path
            path = normalize_path(path)

            if not os.path.exists(path):
                error_msg = f"File {path} does not exist"
                Logger.error(app_logger, f"[insert_text] {error_msg}")
                return FileOperationResult(False, error_msg)

            if insert_line is None:
                error_msg = "No line number specified: insert_line is missing."
                Logger.error(app_logger, f"[insert_text] {error_msg}")
                return FileOperationResult(False, error_msg)

            with open(path, "r") as f:
                lines = f.readlines()

            # Line is 0-indexed for this function, but Claude provides 1-indexed
            insert_line = min(max(0, insert_line - 1), len(lines))

            # Check that the index is within acceptable bounds
            if insert_line < 0 or insert_line > len(lines):
                error_msg = (
                    f"Insert line number {insert_line} out of range (0-{len(lines)})."
                )
                Logger.error(app_logger, f"[insert_text] {error_msg}")
                return FileOperationResult(False, error_msg)

            # Ensure new_str ends with newline
            if new_str and not new_str.endswith("\n"):
                new_str += "\n"

            lines.insert(insert_line, new_str)

            with open(path, "w") as f:
                f.writelines(lines)

            Logger.info(
                app_logger,
                f"[insert_text] Successfully inserted text at line {insert_line + 1} in {path}"
            )
            return FileOperationResult(
                True, f"Successfully inserted text at line {insert_line + 1} in {path}"
            )
        except Exception as e:
            error_msg = f"Error inserting text: {str(e)}"
            Logger.error(app_logger, f"[insert_text] {error_msg}", exc_info=True)
            return FileOperationResult(False, error_msg)

    @staticmethod
    def undo_edit(path: str) -> FileOperationResult:
        """
        Placeholder for undo_edit functionality.
        In a real implementation, you would need to track edit history.

        Args:
            path: The path to the file whose last edit should be undone

        Returns:
            FileOperationResult with message about undo functionality
        """
        try:
            if not path or not path.strip():
                error_msg = "Invalid file path provided: path is empty."
                Logger.error(app_logger, f"[undo_edit] {error_msg}")
                return FileOperationResult(False, error_msg)

            # Normalize the path
            path = normalize_path(path)

            message = "Undo functionality is not implemented in this version."
            Logger.warning(app_logger, f"[undo_edit] {message}")
            return FileOperationResult(True, message)
        except Exception as e:
            error_msg = f"Error in undo_edit: {str(e)}"
            Logger.error(app_logger, f"[undo_edit] {error_msg}", exc_info=True)
            return FileOperationResult(False, error_msg)
