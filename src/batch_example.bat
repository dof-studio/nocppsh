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
