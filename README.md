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
        fe=None,  # Defaults to "./build/benchmark.exe"
        working_dir=".",  # Current directory
        compiler_flags=additional_compiler_flags,
        linker_flags=additional_linker_flags,
        mode="release",  # Can be "release" or "debug",
        architecture="x64"  # Can be "x64" or "x86"
    )
    # The MSVC and VC versions can be automatically detected if left None

    # Call the function with default parameters (debug mode)
    execute_executable(r".\build\x64\**your_file_name**.exe")
```

# An Example Batch file
```batch
    SET VCVARSALL_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat
    
    CALL "%VCVARSALL_PATH%" x64
    
    cl  /O2 /Ot /GL /Ob2 /Gm- /GS- /MP /EHsc /fp:precise /arch:AVX2 ^
        /I"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\10.0.22000.0\include" ^
        /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\ucrt" ^
        /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\shared" ^
        /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\um" ^
        /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\winrt" ^
        /Fo".\build\x64\benchmark.obj" ^
        /Fe".\build\x64\benchmark.exe" ^
        ".\bechmark.cpp" ^
        /link  /LTCG /OPT:REF /OPT:ICF ^
        /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22000.0\ucrt\x64" ^
        /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22000.0\um\x64" ^
        /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x64" 
    
    pause
```
