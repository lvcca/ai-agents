FileSystemSchema = [
    {
        "name": "filesystem.list_directory",
        "description": "List files and directories inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["file", "directory"]
                            },
                            "size": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        }
    },

    {
        "name": "filesystem.read_file",
        "description": "Read a UTF-8 text file inside the workspace. Maximum read size should be limited by the implementation.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "content": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.write_file",
        "description": "Write UTF-8 text content to a file inside the workspace. Creates parent directories if needed.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path inside the workspace root."
                },
                "content": {
                    "type": "string",
                    "description": "UTF-8 text content to write."
                }
            },
            "required": ["path", "content"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "path": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.append_file",
        "description": "Append UTF-8 text content to a file inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path inside the workspace root."
                },
                "content": {
                    "type": "string",
                    "description": "UTF-8 text content to append."
                }
            },
            "required": ["path", "content"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "path": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.create_directory",
        "description": "Create a directory inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative directory path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "path": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.move_file",
        "description": "Move or rename a file inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {
                    "type": "string",
                    "description": "Source file path inside the workspace."
                },
                "dst": {
                    "type": "string",
                    "description": "Destination file path inside the workspace."
                }
            },
            "required": ["src", "dst"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "src": {
                    "type": "string"
                },
                "dst": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.copy_file",
        "description": "Copy a file inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {
                    "type": "string",
                    "description": "Source file path inside the workspace."
                },
                "dst": {
                    "type": "string",
                    "description": "Destination file path inside the workspace."
                }
            },
            "required": ["src", "dst"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "src": {
                    "type": "string"
                },
                "dst": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.delete_file",
        "description": "Delete a file inside the workspace. This operation may be irreversible.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "path": {
                    "type": "string"
                }
            }
        }
    },

    {
        "name": "filesystem.file_exists",
        "description": "Check whether a file or directory exists inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "exists": {
                    "type": "boolean"
                }
            }
        }
    },

    {
        "name": "filesystem.search_files",
        "description": "Search for files inside the workspace by filename pattern.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to search inside."
                },
                "pattern": {
                    "type": "string",
                    "description": "Filename pattern such as '*.py'."
                }
            },
            "required": ["directory"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    },

    {
        "name": "filesystem.get_file_metadata",
        "description": "Retrieve metadata about a file inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path inside the workspace root."
                }
            },
            "required": ["path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "size": {
                    "type": "integer"
                },
                "modified_time": {
                    "type": "string"
                },
                "is_directory": {
                    "type": "boolean"
                }
            }
        }
    },

    {
        "name": "filesystem.read_text_chunks",
        "description": "Read a portion of a text file by line range inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative text file path inside the workspace root."
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number."
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number."
                }
            },
            "required": ["path", "start_line", "end_line"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string"
                },
                "start_line": {
                    "type": "integer"
                },
                "end_line": {
                    "type": "integer"
                }
            }
        }
    }
]
