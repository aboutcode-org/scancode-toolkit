{
    "new_rules": [
        {
            "name": "cpp_files01",
            "test": "all(extension == resource.extension for extension in ['.cpp']) & any(file_type == resource.file_type for file_type in ['C source, ASCII text', 'C++ source, ASCII text', 'ASCII text'])",
            "domain": "general",
            "status": "core code"
        },
        {
            "name": "cpp_files_c_extension01",
            "test": "all(extension == resource.extension for extension in ['.c']) & any(file_type == resource.file_type for file_type in ['C source, ASCII text']) & all(programming_language == resource.programming_language for programming_language in ['C++'])",
            "domain": "general",
            "status": "core code"
        },
        {
            "name": "cpp_files_header01",
            "test": "all(extension == resource.extension for extension in ['.h']) & any(file_type == resource.file_type for file_type in ['ASCII text', 'C++ source, ASCII text', 'C source, ASCII text'])",
            "domain": "general",
            "status": "core code"
        },
        {
            "name": "map_files01",
            "test": "all(extension == resource.extension for extension in ['.map']) & any(file_type == resource.file_type for file_type in ['ASCII text'])",
            "domain": "general",
            "status": "non-core JavaScript map file"
        },
        {
            "name": "Blueprint_files01",
            "test": "all(extension == resource.extension for extension in ['.bp']) & any(file_type == resource.file_type for file_type in ['ASCII text'])",
            "domain": "general",
            "status": "non-core build configuration"
        }
    ]
}
