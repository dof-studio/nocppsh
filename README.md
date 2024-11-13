# clit
Too hard to call cl.exe to compile, link, and run MSVC small projects? Using cpp.sh, but too slow? Here: clit can automatically configure your input c++ source files and generate a batch file to compile in one-shot. Try it!

# How to use it?
```python

    # Define the list of source files
    source_files = [
        # Add more source files here
    ]
    
    # Define additional compiler flags (if any)
    additional_compiler_flags = {
        # Example: "/favor:Intel64": "",
        # Add other compiler flags as needed
    }
    
    # Define additional linker flags (if any)
    additional_linker_flags = {
        # Example: "/NODEFAULTLIB:library": "",
        # Add other linker flags as needed
    }
    
    # Call the function with default parameters (release mode)
    compile_sources(
        src_files=source_files,
        fo=None,  # Defaults to "./build"
        fe=None,  # Defaults to "./build/benchmark-box-cpp.exe"
        working_dir=".",  # Current directory
        compiler_flags=additional_compiler_flags,
        linker_flags=additional_linker_flags,
        mode="release",  # Can be "release" or "debug",
        architecture="x64"  # Can be "x64" or "x86"
    )

    # Call the function with default parameters (debug mode)
    execute_executable(r".\build\x64\**your_file_name**.exe")
```
