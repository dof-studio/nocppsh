'''
auto-compiler-cpp.py
version 0.0.1 built 241113
DOF Studio
'''

import os
import re
import sys
import winreg
import subprocess
from typing import List, Dict, Optional


# Detect Visual Studio versions
def detect_vs_versions(
    vswhere_path: Optional[str] = None
) -> List[str]:
    """
    Detects installed Visual Studio versions on a Windows system.

    Parameters:
    - vswhere_path (Optional[str]): The file path to vswhere.exe. If None,
      the function will attempt to locate vswhere.exe in the default installation path.

    Returns:
    - List[str]: A list of detected Visual Studio version numbers as strings.
                 Example: ["2010", "2017", "2019", "2022"]
    """
    detected_versions = set()

    # Helper function to add versions to the set
    def add_version(version: str):
        if version:
            detected_versions.add(version)

    # 1. Use vswhere.exe for Visual Studio 2017 and later
    def use_vswhere(vswhere_exe: str):
        try:
            # Execute vswhere.exe to get all installations
            result = subprocess.run(
                [vswhere_exe, "-latest", "-products", "*", "-format", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            import json
            installations = json.loads(result.stdout)
            for install in installations:
                # Extract the major version number from 'installationVersion'
                installation_version = install.get("installationVersion", "")
                if installation_version:
                    major_version = installation_version.split(".")[0]
                    add_version(major_version)
        except subprocess.CalledProcessError as e:
            print(f"Error executing vswhere.exe: {e}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"Error parsing vswhere.exe output: {e}", file=sys.stderr)

    # Locate vswhere.exe if not provided
    if vswhere_path is None:
        default_vswhere_path = os.path.join(
            os.environ.get("ProgramFiles(x86)", ""),
            "Microsoft Visual Studio",
            "Installer",
            "vswhere.exe"
        )
        if os.path.exists(default_vswhere_path):
            vswhere_path = default_vswhere_path
        else:
            vswhere_path = None

    if vswhere_path and os.path.exists(vswhere_path):
        use_vswhere(vswhere_path)
    else:
        print("vswhere.exe not found. Skipping detection for Visual Studio 2017 and later.", file=sys.stderr)

    # 2. Query the Windows Registry for older Visual Studio versions
    def query_registry_for_vs():
        """
        Queries the Windows Registry to find older Visual Studio installations (2010, 2012, 2013, 2015).
        """
        vs_registry_keys = {
            "2010": r"SOFTWARE\Microsoft\VisualStudio\10.0",
            "2012": r"SOFTWARE\Microsoft\VisualStudio\11.0",
            "2013": r"SOFTWARE\Microsoft\VisualStudio\12.0",
            "2015": r"SOFTWARE\Microsoft\VisualStudio\14.0",
            "2017": r"SOFTWARE\Microsoft\VisualStudio\15.0",
            "2019": r"SOFTWARE\Microsoft\VisualStudio\16.0",
            "2022": r"SOFTWARE\Microsoft\VisualStudio\17.0",
        }

        # For 32-bit Python on 64-bit Windows, access the 64-bit registry view
        registry_views = [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]

        for version, reg_path in vs_registry_keys.items():
            for view in registry_views:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ | view) as key:
                        # If the key exists, Visual Studio is installed
                        add_version(version)
                        break  # No need to check other views
                except FileNotFoundError:
                    continue  # Try the next view or version
                except PermissionError:
                    print(f"Permission denied accessing registry key for VS {version}.", file=sys.stderr)
                except Exception as e:
                    print(f"Error accessing registry for VS {version}: {e}", file=sys.stderr)

    query_registry_for_vs()

    return sorted(detected_versions, key=lambda x: int(x))


# Detect MSVC versions
def detect_msvc_versions(
    visual_studio_path: str = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
    windows_kits_path: str = r"C:\Program Files (x86)\Windows Kits\10\Include"
) -> List[str]:
    """
    Detects available MSVC version numbers for MSVC toolsets and Windows SDKs.
    
    Parameters:
    - visual_studio_path (str): Path to the MSVC toolset directory.
    - windows_kits_path (str): Path to the Windows Kits Include directory.
    
    Returns:
    - List[str]: A list of detected version strings.
    """
    
    version_pattern = re.compile(r'^\d+\.\d+\.\d+\.\d+$')
    detected_versions = []
    
    # Helper function to scan a directory for versioned subdirectories
    def scan_versions(base_path: str, is_lib: bool = False) -> List[str]:
        versions = []
        if not os.path.exists(base_path):
            print(f"Directory does not exist: {base_path}")
            return versions
        
        try:
            for entry in os.listdir(base_path):
                entry_path = os.path.join(base_path, entry)
                if os.path.isdir(entry_path) and version_pattern.match(entry):
                    versions.append(entry)
        except Exception as e:
            print(f"Error accessing {base_path}: {e}")
        
        return versions
    
    # Scan Visual Studio MSVC versions
    mscc_versions = scan_versions(visual_studio_path)
    if mscc_versions:
        print(f"Detected MSVC Versions in '{visual_studio_path}': {mscc_versions}")
        detected_versions.extend(mscc_versions)
    else:
        print(f"No MSVC versions found in '{visual_studio_path}'.")
    
    # Scan Windows SDK versions
    windows_sdk_versions = scan_versions(windows_kits_path)
    if windows_sdk_versions:
        print(f"Detected Windows SDK Versions in '{windows_kits_path}': {windows_sdk_versions}")
        detected_versions.extend(windows_sdk_versions)
    else:
        print(f"No Windows SDK versions found in '{windows_kits_path}'.")
    
    return detected_versions


# Generate build.bat file
def generate_compile_bat(
    src_files: List[str],
    fo: Optional[str] = None,
    fe: Optional[str] = None,
    working_dir: str = ".",
    compiler_flags: Optional[Dict[str, str]] = None,
    linker_flags: Optional[Dict[str, str]] = None,
    vs_version: Optional[str] = None,
    msvc_version: Optional[str] = None,
    mode: str = "release",
    architecture: str = "x64",
) -> None:
    """
    Compiles C++ source files using Microsoft's cl.exe compiler by generating and executing a build.bat file.
    
    Parameters:
    - src_files (List[str]): List of paths to the C++ source files to compile.
    - fo (Optional[str]): The /Fo parameter specifying the output directory for object files. Defaults to "./build".
    - fe (Optional[str]): The /Fe parameter specifying the output executable file path. Defaults to "./build/benchmark-box-cpp.exe".
    - working_dir (str): The directory where the build.bat file will be created. Defaults to the current directory "./".
    - compiler_flags (Optional[Dict[str, str]]): Additional compiler flags as a dictionary.
    - linker_flags (Optional[Dict[str, str]]): Additional linker flags as a dictionary.
    - vs_version (Optional[str]): The Visual Studio version to use for compilation. Defaults to the latest detected version.
    - msvc_version (Optional[str]): The MSVC version to use for compilation. Defaults to the latest detected version.
    - mode (str): Build mode, either "release" or "debug". Defaults to "release".
    - architecture (str): Target architecture, either "x64" or "x86". Defaults to "x64".
    """
    
    
    # Define presets for release and debug modes
    presets = {
        "release": {
            "compiler": {
                "/O2": "",
                "/Ot": "",
                "/GL": "",
                "/Ob2": "",
                "/Gm-": "",
                "/GS-": "",
                "/MP": "",
                "/EHsc": "",        # Enable standard C++ exception handling
                "/fp:precise": "",  # Optional: Precise floating-point model
            },
            "linker": {
                "/LTCG": "",
                "/OPT:REF": "",
                "/OPT:ICF": "",
            }
        },
        "debug": {
            "compiler": {
                "/Zi": "",         # Generate complete debugging information
                "/Od": "",         # Disable optimizations
                "/RTC1": "",       # Enable run-time error checks
                "/Gm": "",         # Enable minimal rebuild
                "/EHsc": "",       # Enable standard C++ exception handling
            },
            "linker": {
                "/DEBUG": "",
                "/OPT:NOREF": "",
                "/OPT:NOICF": "",
            }
        }
    }
    
    # Add /arch flag based on architecture
    if architecture == "x64":
        presets["release"]["compiler"]["/arch:AVX2"] = ""
        presets["debug"]["compiler"]["/arch:AVX2"] = ""
    elif architecture == "x86":
        presets["release"]["compiler"]["/arch:SSE2"] = ""
        presets["debug"]["compiler"]["/arch:SSE2"] = ""

    # Validate mode
    if mode not in presets:
        raise ValueError(f"Invalid mode '{mode}'. Supported modes are: {list(presets.keys())}")
    
    # Set default /Fo and /Fe if None
    if fo is None:
        fo = os.path.join(working_dir, "build" + "\\" + architecture)
    if fe is None:
        fe = os.path.join(fo, "benchmark-box-cpp.exe")
    
    # Ensure the build directory exists
    os.makedirs(fo, exist_ok=True)
    
    # Initialize compiler and linker flags based on the mode
    final_compiler_flags = presets[mode]["compiler"].copy()
    final_linker_flags = presets[mode]["linker"].copy()
    
    # Update with additional compiler flags if provided
    if compiler_flags:
        for flag, value in compiler_flags.items():
            final_compiler_flags[flag] = value
    
    # Update with additional linker flags if provided
    if linker_flags:
        for flag, value in linker_flags.items():
            final_linker_flags[flag] = value

    # If vs_version is not specified, use the latest installed version
    if vs_version is None:
        vs_version = detect_vs_versions()
        if len(vs_version) == 0:
            raise ValueError("Visual Studio version not found. Please specify the vs_version parameter or install one manually.")
        elif len(vs_version) > 1:
            vs_version = vs_version[-1]
        elif len(vs_version) == 1: 
            vs_version = vs_version[0]

    # If msvc_version is not specified, use the default version
    if msvc_version is None:
        msvc_version = detect_msvc_versions()
        if len(msvc_version) == 0:
            raise ValueError("MSVC version not found. Please specify the msvc_version parameter or install one manually.")
        elif len(msvc_version) > 1:
            msvc_version = msvc_version[-1]
        elif len(msvc_version) == 1:
            msvc_version = msvc_version[0]

    # Define include paths and lib paths as per user's environment
    include_paths = [
        'C:\\Program Files\\Microsoft Visual Studio\\' + vs_version + '\\Community\\VC\\Tools\\MSVC\\' + msvc_version + '\\include',
        'C:\\Program Files (x86)\\Windows Kits\\10\\Include\\' + msvc_version + '\\ucrt',
        'C:\\Program Files (x86)\\Windows Kits\\10\\Include\\' + msvc_version + '\\shared',
        'C:\\Program Files (x86)\\Windows Kits\\10\\Include\\' + msvc_version + '\\um',
        'C:\\Program Files (x86)\\Windows Kits\\10\\Include\\' + msvc_version + '\\winrt'
    ]
    
    lib_paths = [
        'C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\' + msvc_version + '\\ucrt' + '\\' + architecture,
        'C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\' + msvc_version + '\\um' + '\\' + architecture,
        'C:\\Program Files (x86)\\Windows Kits\\10\\bin\\' + msvc_version + '\\' + architecture,
    ]
    
    # Call vcvarshall.bat to set up the environment
    vcvarshall = [
        "SET VCVARSALL_PATH=C:\\Program Files\\Microsoft Visual Studio\\"+ vs_version + "\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat"
    ]
    vcvarshall.append('')
    if architecture == 'x86':
        vcvarshall.append('CALL "%VCVARSALL_PATH%" x86')
    elif architecture == 'x64':
        vcvarshall.append('CALL "%VCVARSALL_PATH%" x64')
    else:
        raise ValueError("Unsupported architecture. Please use 'x86' or 'x64'.")

    # Start building the batch file content
    batch_lines = vcvarshall
    batch_lines.append('')
    
    # Add compile flags
    compile_tags = 'cl '
    for flag, value in final_compiler_flags.items():
        if value:
            compile_tags += f' {flag} {value}'
        else:
            compile_tags += f' {flag}'
    compile_tags += ' ^'
    batch_lines.append(compile_tags)
    
    # Add include paths
    for include in include_paths:
        batch_lines.append(f'    /I"{include}" ^')
    
    # Add /Fo and /Fe
    if len(src_files) == 1:
        obj_name = os.path.splitext(os.path.basename(src_files[0]))[0] + ".obj"
        fo_param = f'/Fo"{os.path.join(fo, obj_name)}" ^'
    else:
        # Ensure fo ends with a backslash
        fo_dir = fo if fo.endswith('\\') else fo + '\\'
        fo_param = f'/Fo"{fo_dir}" ^'
    batch_lines.append(f'    {fo_param}')
    
    batch_lines.append(f'    /Fe"{fe}" ^')
    
    # Add source files
    for src in src_files:
        batch_lines.append(f'    "{src}" ^')
    
    # Add linker flags
    linker_tags = '    /link '
    for flag, value in final_linker_flags.items():
        if value:
            linker_tags += f' {flag} {value}'
        else:
            linker_tags += f' {flag}'
    linker_tags += ' ^'
    batch_lines.append(linker_tags)
    
    # Add lib paths
    for lib in lib_paths:
        batch_lines.append(f'    /LIBPATH:"{lib}" ^')
    
    # Remove the trailing caret and add newline
    if batch_lines[-1].endswith('^'):
        batch_lines[-1] = batch_lines[-1][:-1]
    
    # Add pause at the end
    batch_lines.append('')
    batch_lines.append('pause')
    
    # Join all lines into a single string
    batch_content = '\n'.join(batch_lines)
    
    # Define the path for build.bat
    build_bat_path = os.path.join(working_dir, "build.bat")
    
    # Write the batch file
    with open(build_bat_path, 'w') as bat_file:
        bat_file.write(batch_content)
    
    print(f"Generated {build_bat_path}")
    
    return build_bat_path


# Build by the bat file using cl.exe   
def build_by_cl(
    build_bat_path):
    '''
    build_bat_path: Path to the build.bat file generated by build_batch_file
    '''

    # Execute the batch file
    try:
        print("Starting compilation...")
        subprocess.run(['cmd', '/c', build_bat_path], check=True)
        print("Compilation finished successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred during compilation.")
        print(e)

    return build_bat_path


# Combined function to compile C++ source files
def compile_sources(
    src_files: List[str],
    fo: Optional[str] = None,
    fe: Optional[str] = None,
    working_dir: str = ".",
    compiler_flags: Optional[Dict[str, str]] = None,
    linker_flags: Optional[Dict[str, str]] = None,
    vs_version: Optional[str] = None,
    msvc_version: Optional[str] = None,
    mode: str = "release",
    architecture: str = "x64",
) -> None:
    """
    Compiles C++ source files using Microsoft's cl.exe compiler by generating and executing a build.bat file.
    Run the build.bat file to execute the compilation.
    
    Parameters:
    - src_files (List[str]): List of paths to the C++ source files to compile.
    - fo (Optional[str]): The /Fo parameter specifying the output directory for object files. Defaults to "./build".
    - fe (Optional[str]): The /Fe parameter specifying the output executable file path. Defaults to "./build/benchmark-box-cpp.exe".
    - working_dir (str): The directory where the build.bat file will be created. Defaults to the current directory "./".
    - compiler_flags (Optional[Dict[str, str]]): Additional compiler flags as a dictionary.
    - linker_flags (Optional[Dict[str, str]]): Additional linker flags as a dictionary.
    - vs_version (Optional[str]): The Visual Studio version to use for compilation. Defaults to the latest detected version.
    - msvc_version (Optional[str]): The MSVC version to use for compilation. Defaults to the latest detected version.
    - mode (str): Build mode, either "release" or "debug". Defaults to "release".
    - architecture (str): Target architecture, either "x64" or "x86". Defaults to "x64".
    """
    
    build_bat_path = generate_compile_bat(
        src_files=src_files,
        fo=fo,
        fe=fe,
        working_dir=working_dir,
        compiler_flags=compiler_flags,
        linker_flags=linker_flags,
        vs_version=vs_version,
        msvc_version=msvc_version,
        mode=mode,
        architecture=architecture
    )

    # If path exists, build
    if os.path.exists(build_bat_path):
        build_by_cl(build_bat_path)
        return build_bat_path
    else:
        print(f"{build_bat_path} not found. Compilation aborted.", build_bat_path)
        return None


# Execute executable files
def execute_executable(
    executable_path: str) -> None:
    '''
    executable_path (str): The path to the executable file to execute.
    '''
    # Execute the exe
    try:
        print("Starting execution...")
        subprocess.run(['cmd', '/c', executable_path], check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred during execution.")
        print(e)

    return executable_path


# Entrypoint
if __name__ == "__main__":
    # Define the list of source files
    source_files = [
        r"example.cpp"
        # Add more source files here if needed
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
        fe=None,  # Defaults to "./build/example.exe"
        working_dir=".",  # Current directory
        compiler_flags=additional_compiler_flags,
        linker_flags=additional_linker_flags,
        mode="release",  # Can be "release" or "debug",
        architecture="x64"  # Can be "x64" or "x86"
    )

    # Call the function with default parameters (debug mode)
    execute_executable(r".\build\x64\example.exe")

